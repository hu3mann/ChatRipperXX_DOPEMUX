"""Performance benchmarking framework for embedding models."""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import gc

from .base import BaseEmbeddingProvider, EmbeddingMetrics


logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuration for embedding model benchmarks."""
    
    num_texts: int = 1000
    text_lengths: List[int] = field(default_factory=lambda: [50, 150, 300])
    batch_sizes: List[int] = field(default_factory=lambda: [1, 16, 32, 64])
    warmup_runs: int = 3
    measurement_runs: int = 5
    include_memory_profiling: bool = True


@dataclass
class BenchmarkResult:
    """Results from embedding model benchmark."""
    
    model_name: str
    device: str
    avg_time_per_text: float
    throughput_texts_per_second: float
    peak_memory_mb: float
    batch_performance: Dict[int, float]  # batch_size -> time_per_text
    dimension: int


class BenchmarkRunner:
    """Runs performance benchmarks on embedding providers."""
    
    def __init__(self, config: BenchmarkConfig):
        """Initialize benchmark runner.
        
        Args:
            config: Benchmark configuration
        """
        self.config = config
    
    async def run_benchmark(self, provider: BaseEmbeddingProvider, 
                          device: str) -> BenchmarkResult:
        """Run comprehensive benchmark on a provider.
        
        Args:
            provider: Embedding provider to benchmark
            device: Device being used for inference
            
        Returns:
            BenchmarkResult with performance metrics
        """
        model_info = provider.get_model_info()
        logger.info(f"Benchmarking {model_info.name} on {device}")
        
        # Generate test corpus
        test_texts = create_test_corpus(
            self.config.num_texts, 
            self.config.text_lengths
        )
        
        # Warmup runs
        await self._run_warmup(provider, test_texts[:100])
        
        # Measure single text performance
        single_perf = await self._measure_single_performance(provider, test_texts)
        
        # Measure batch performance 
        batch_perf = await self._measure_batch_performance(provider, test_texts)
        
        # Calculate throughput
        throughput = 1.0 / single_perf if single_perf > 0 else 0.0
        
        return BenchmarkResult(
            model_name=model_info.name,
            device=device,
            avg_time_per_text=single_perf,
            throughput_texts_per_second=throughput,
            peak_memory_mb=0.0,  # TODO: Implement memory profiling
            batch_performance=batch_perf,
            dimension=provider.get_embedding_dimension()
        )
    
    async def compare_models(self, providers: List[BaseEmbeddingProvider],
                           devices: List[str]) -> 'ModelComparison':
        """Compare multiple embedding providers.
        
        Args:
            providers: List of embedding providers
            devices: List of devices to test on
            
        Returns:
            ModelComparison with results
        """
        results = []
        
        for provider, device in zip(providers, devices):
            try:
                result = await self.run_benchmark(provider, device)
                results.append(result)
            except Exception as e:
                logger.error(f"Benchmark failed for {provider}: {e}")
        
        return ModelComparison(results)
    
    async def _run_warmup(self, provider: BaseEmbeddingProvider, 
                         texts: List[str]) -> None:
        """Run warmup to stabilize performance."""
        logger.debug(f"Running {self.config.warmup_runs} warmup runs")
        
        for _ in range(self.config.warmup_runs):
            # Mix single and batch operations
            await provider.encode(texts[0])
            await provider.encode_batch(texts[:16])
            gc.collect()  # Force garbage collection between runs
    
    async def _measure_single_performance(self, provider: BaseEmbeddingProvider,
                                        texts: List[str]) -> float:
        """Measure single text encoding performance."""
        times = []
        sample_texts = random.sample(texts, min(100, len(texts)))
        
        for _ in range(self.config.measurement_runs):
            start_time = time.perf_counter()
            
            for text in sample_texts:
                await provider.encode(text)
            
            elapsed = time.perf_counter() - start_time
            times.append(elapsed / len(sample_texts))
        
        return sum(times) / len(times)
    
    async def _measure_batch_performance(self, provider: BaseEmbeddingProvider,
                                       texts: List[str]) -> Dict[int, float]:
        """Measure batch encoding performance for different batch sizes."""
        batch_performance = {}
        
        for batch_size in self.config.batch_sizes:
            if batch_size > len(texts):
                continue
                
            times = []
            
            for _ in range(self.config.measurement_runs):
                batch_texts = random.sample(texts, batch_size)
                
                start_time = time.perf_counter()
                await provider.encode_batch(batch_texts)
                elapsed = time.perf_counter() - start_time
                
                times.append(elapsed / batch_size)  # Time per text
            
            batch_performance[batch_size] = sum(times) / len(times)
        
        return batch_performance


class ModelComparison:
    """Comparison of multiple embedding model benchmark results."""
    
    def __init__(self, results: List[BenchmarkResult]):
        """Initialize comparison with benchmark results.
        
        Args:
            results: List of benchmark results to compare
        """
        self.results = results
        
        # Calculate comparison metrics
        self.fastest_model = min(results, key=lambda r: r.avg_time_per_text).model_name
        self.highest_throughput = max(results, key=lambda r: r.throughput_texts_per_second).model_name
        self.lowest_memory = min(results, key=lambda r: r.peak_memory_mb).model_name
    
    def get_recommendation(self, priority: str = "balanced") -> BenchmarkResult:
        """Get model recommendation based on priority.
        
        Args:
            priority: Priority for recommendation ("speed", "quality", "memory", "balanced")
            
        Returns:
            Recommended benchmark result
        """
        if priority == "speed":
            return min(self.results, key=lambda r: r.avg_time_per_text)
        elif priority == "quality":
            # Prefer higher dimensional models as proxy for quality
            return max(self.results, key=lambda r: r.dimension)
        elif priority == "memory":
            return min(self.results, key=lambda r: r.peak_memory_mb)
        else:  # balanced
            # Weighted score considering speed and dimension
            def balanced_score(result: BenchmarkResult) -> float:
                speed_score = 1.0 / result.avg_time_per_text
                quality_score = result.dimension / 1024.0  # Normalize
                return speed_score * 0.6 + quality_score * 0.4
            
            return max(self.results, key=balanced_score)
    
    def generate_report(self) -> str:
        """Generate human-readable comparison report.
        
        Returns:
            Formatted comparison report
        """
        lines = ["Embedding Model Benchmark Comparison", "=" * 40, ""]
        
        for result in sorted(self.results, key=lambda r: r.avg_time_per_text):
            lines.append(f"Model: {result.model_name}")
            lines.append(f"  Device: {result.device}")
            lines.append(f"  Avg time per text: {result.avg_time_per_text:.4f}s")
            lines.append(f"  Throughput: {result.throughput_texts_per_second:.1f} texts/sec")
            lines.append(f"  Peak memory: {result.peak_memory_mb:.1f}MB")
            lines.append(f"  Dimension: {result.dimension}")
            lines.append("")
        
        lines.extend([
            "Summary:",
            f"  Fastest: {self.fastest_model}",
            f"  Highest throughput: {self.highest_throughput}",
            f"  Lowest memory: {self.lowest_memory}"
        ])
        
        return "\n".join(lines)


def create_test_corpus(num_texts: int = 1000, 
                      text_lengths: Optional[List[int]] = None) -> List[str]:
    """Create a test corpus for benchmarking.
    
    Args:
        num_texts: Number of texts to generate
        text_lengths: Target lengths for generated texts
        
    Returns:
        List of test texts
    """
    if text_lengths is None:
        text_lengths = [50, 150, 300]
    
    # Sample conversational patterns
    patterns = [
        "Hey {name}, how was your {event} today?",
        "Thanks for {action}, really appreciate it!",
        "What do you think about {topic}? I'm curious to hear your perspective.",
        "Just wanted to check in and see how you're doing with {situation}.",
        "Can you help me understand {concept}? I'm having trouble with it.",
        "I love how you {quality}. It always makes me feel better.",
        "Remember when we {memory}? That was such a great time.",
        "I'm excited about {future_event}. Are you planning to {action}?",
        "Sorry about {mistake}. I'll make sure to {resolution} next time.",
        "Your advice about {topic} really helped me with {outcome}."
    ]
    
    # Sample words for filling patterns
    names = ["Alex", "Sam", "Jordan", "Casey", "Riley", "Taylor"]
    events = ["meeting", "interview", "presentation", "workout", "class"]
    actions = ["helping out", "being there", "listening", "understanding"]
    topics = ["work", "travel", "hobbies", "goals", "relationships"]
    situations = ["the new job", "moving", "the project", "family stuff"]
    
    corpus = []
    
    for _ in range(num_texts):
        # Choose target length
        target_length = random.choice(text_lengths)
        
        # Start with a pattern
        pattern = random.choice(patterns)
        text = pattern.format(
            name=random.choice(names),
            event=random.choice(events),
            action=random.choice(actions),
            topic=random.choice(topics),
            situation=random.choice(situations),
            concept=random.choice(topics),
            quality="explain things so clearly",
            memory="went to the concert",
            future_event="the weekend trip",
            mistake="yesterday's confusion",
            resolution="double-check everything",
            outcome="my presentation"
        )
        
        # Extend or trim to target length
        while len(text) < target_length:
            text += f" I think it's important to remember that {random.choice(topics)} can really make a difference."
        
        if len(text) > target_length:
            # Truncate at word boundary
            words = text[:target_length].split()
            if words:
                text = " ".join(words[:-1])
        
        corpus.append(text)
    
    return corpus