"""Advanced performance optimization for local LLM inference.

This module provides comprehensive performance monitoring, adaptive optimization,
and benchmarking capabilities for Ollama-based local model inference.
"""

import asyncio
import json
import logging
import os
import psutil
import platform
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SystemResources:
    """Current system resource utilization."""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    gpu_utilization: float = 0.0  # 0-100%
    gpu_memory_used_gb: float = 0.0
    gpu_memory_total_gb: float = 0.0
    disk_io_read_mb_s: float = 0.0
    disk_io_write_mb_s: float = 0.0
    
    @property
    def is_memory_constrained(self) -> bool:
        """Check if system is memory constrained."""
        return self.memory_percent > 85.0 or self.memory_available_gb < 2.0
    
    @property
    def is_gpu_memory_constrained(self) -> bool:
        """Check if GPU memory is constrained."""
        if self.gpu_memory_total_gb > 0:
            return (self.gpu_memory_used_gb / self.gpu_memory_total_gb) > 0.9
        return False


@dataclass
class ModelBenchmark:
    """Benchmark results for a specific model configuration."""
    model_name: str
    quantization: str
    context_window: int
    batch_size: int
    concurrent_requests: int
    
    # Performance metrics
    throughput_msgs_per_second: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_tokens_per_second: float
    memory_peak_gb: float
    
    # Quality metrics (optional)
    schema_validation_rate: float = 1.0
    confidence_avg: float = 0.0
    
    # System info
    timestamp: str = ""
    system_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.system_info is None:
            self.system_info = {}
    
    @property
    def meets_nfr_targets(self) -> bool:
        """Check if benchmark meets NFR targets."""
        return (
            self.throughput_msgs_per_second >= 25.0 and
            self.p95_latency_ms <= 250.0 and
            self.schema_validation_rate >= 0.95
        )


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    category: str  # "model", "system", "configuration"
    recommendation: str
    expected_improvement: str
    priority: str  # "critical", "high", "medium", "low"
    implementation_effort: str  # "trivial", "easy", "moderate", "complex"


class SystemMonitor:
    """Real-time system resource monitoring."""
    
    def __init__(self, sample_interval: float = 1.0):
        self.sample_interval = sample_interval
        self.baseline_io: Optional[Tuple[int, int]] = None
        self._monitoring = False
        
    async def get_current_resources(self) -> SystemResources:
        """Get current system resource utilization."""
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_available_gb = memory.available / (1024**3)
        
        # GPU metrics (if available)
        gpu_utilization = 0.0
        gpu_memory_used_gb = 0.0
        gpu_memory_total_gb = 0.0
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    gpu_utilization = gpu.load * 100
                    gpu_memory_used_gb = gpu.memoryUsed / 1024
                    gpu_memory_total_gb = gpu.memoryTotal / 1024
            except Exception as e:
                logger.debug(f"GPU monitoring failed: {e}")
        
        # Disk I/O
        disk_io_read_mb_s = 0.0
        disk_io_write_mb_s = 0.0
        
        try:
            if self.baseline_io is None:
                self.baseline_io = psutil.disk_io_counters()[:2]  # read_bytes, write_bytes
                await asyncio.sleep(self.sample_interval)
            
            current_io = psutil.disk_io_counters()
            if current_io and self.baseline_io:
                read_diff = current_io.read_bytes - self.baseline_io[0]
                write_diff = current_io.write_bytes - self.baseline_io[1]
                
                disk_io_read_mb_s = read_diff / (1024**2) / self.sample_interval
                disk_io_write_mb_s = write_diff / (1024**2) / self.sample_interval
                
                self.baseline_io = (current_io.read_bytes, current_io.write_bytes)
                
        except Exception as e:
            logger.debug(f"Disk I/O monitoring failed: {e}")
        
        return SystemResources(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_gb=memory_available_gb,
            gpu_utilization=gpu_utilization,
            gpu_memory_used_gb=gpu_memory_used_gb,
            gpu_memory_total_gb=gpu_memory_total_gb,
            disk_io_read_mb_s=disk_io_read_mb_s,
            disk_io_write_mb_s=disk_io_write_mb_s,
        )


class ModelBenchmarker:
    """Comprehensive model benchmarking and performance analysis."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("./.benchmark_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.system_monitor = SystemMonitor()
        
        # Benchmark configurations to test
        self.benchmark_configs = [
            # Gemma2 variants
            {
                "model": "gemma2:9b-instruct-q4_K_M",
                "quantization": "Q4_K_M",
                "context_window": 4096,
                "batch_sizes": [1, 2, 4, 8],
                "concurrent_requests": [2, 4, 6, 8],
            },
            {
                "model": "gemma2:9b-instruct-q4_K_S",
                "quantization": "Q4_K_S", 
                "context_window": 4096,
                "batch_sizes": [1, 2, 4, 8],
                "concurrent_requests": [2, 4, 6, 8],
            },
            {
                "model": "gemma2:9b-instruct-q5_K_M", 
                "quantization": "Q5_K_M",
                "context_window": 4096,
                "batch_sizes": [1, 2, 4],  # Smaller batches for higher quality
                "concurrent_requests": [2, 4, 6],
            },
            # Lightweight alternatives
            {
                "model": "gemma2:2b-instruct-q4_K_M",
                "quantization": "Q4_K_M",
                "context_window": 4096,
                "batch_sizes": [2, 4, 8, 16],
                "concurrent_requests": [4, 8, 12, 16],
            },
        ]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "cpu_cores_physical": psutil.cpu_count(logical=False),
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "gpu_info": self._get_gpu_info(),
            "python_version": platform.python_version(),
            "benchmark_timestamp": datetime.now().isoformat(),
        }
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
        gpu_info = {"available": False}
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_info = {
                        "available": True,
                        "name": gpu.name,
                        "memory_total_gb": gpu.memoryTotal / 1024,
                        "driver_version": gpu.driver,
                    }
            except Exception as e:
                logger.debug(f"Failed to get GPU info: {e}")
        
        return gpu_info
    
    async def benchmark_model_config(
        self,
        ollama_client,
        model_config: Dict[str, Any],
        sample_prompts: List[str],
        duration_seconds: int = 60
    ) -> List[ModelBenchmark]:
        """Benchmark a specific model configuration."""
        logger.info(f"Benchmarking model: {model_config['model']}")
        
        benchmarks = []
        
        for batch_size in model_config["batch_sizes"]:
            for concurrent in model_config["concurrent_requests"]:
                logger.info(f"Testing batch_size={batch_size}, concurrent={concurrent}")
                
                try:
                    benchmark = await self._run_benchmark(
                        ollama_client=ollama_client,
                        model_name=model_config["model"],
                        quantization=model_config["quantization"],
                        context_window=model_config["context_window"],
                        batch_size=batch_size,
                        concurrent_requests=concurrent,
                        sample_prompts=sample_prompts,
                        duration_seconds=duration_seconds
                    )
                    
                    benchmarks.append(benchmark)
                    
                    # Save intermediate results
                    self._save_benchmark_result(benchmark)
                    
                    # Cool-down period between benchmarks
                    await asyncio.sleep(2.0)
                    
                except Exception as e:
                    logger.error(f"Benchmark failed for {model_config['model']} "
                               f"(batch={batch_size}, concurrent={concurrent}): {e}")
                    continue
        
        return benchmarks
    
    async def _run_benchmark(
        self,
        ollama_client,
        model_name: str,
        quantization: str,
        context_window: int,
        batch_size: int,
        concurrent_requests: int,
        sample_prompts: List[str],
        duration_seconds: int
    ) -> ModelBenchmark:
        """Run a single benchmark configuration."""
        
        # Configure the client for this benchmark
        ollama_client.max_concurrent = concurrent_requests
        ollama_client.model_config.name = model_name
        ollama_client.model_config.context_window = context_window
        
        # Reset metrics
        ollama_client.metrics = ollama_client.__class__.PerformanceMetrics()
        ollama_client.latencies.clear()
        
        # Monitor system resources
        initial_resources = await self.system_monitor.get_current_resources()
        memory_peak_gb = initial_resources.memory_available_gb
        
        # Generate test requests
        test_requests = []
        prompt_cycle = 0
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        latencies = []
        total_requests = 0
        successful_requests = 0
        total_tokens = 0
        validation_failures = 0
        confidence_scores = []
        
        logger.info(f"Starting {duration_seconds}s benchmark...")
        
        # Run benchmark for specified duration
        while time.time() < end_time:
            batch_requests = []
            
            for _ in range(batch_size):
                prompt = sample_prompts[prompt_cycle % len(sample_prompts)]
                test_requests.append({
                    "text": prompt,
                    "request_id": f"bench_{total_requests}",
                })
                batch_requests.append(test_requests[-1])
                prompt_cycle += 1
                total_requests += 1
            
            # Process batch
            batch_start = time.time()
            
            try:
                # Simulate enrichment request (simplified)
                from chatx.enrichment.models import EnrichmentRequest, BatchEnrichmentRequest
                
                requests = [EnrichmentRequest(text=req["text"], msg_id=req["request_id"]) 
                           for req in batch_requests]
                batch_request = BatchEnrichmentRequest(requests=requests)
                
                batch_response = await ollama_client.enrich_batch(batch_request)
                
                batch_latency = (time.time() - batch_start) * 1000  # ms
                latencies.append(batch_latency)
                
                # Analyze responses
                for response in batch_response.responses:
                    if response.error is None and response.enrichment is not None:
                        successful_requests += 1
                        
                        # Estimate tokens (rough)
                        total_tokens += len(response.enrichment.model_dump_json().split())
                        
                        # Track confidence
                        if hasattr(response.enrichment, 'confidence_llm'):
                            confidence_scores.append(response.enrichment.confidence_llm)
                        
                        # Validate schema (simplified check)
                        try:
                            response.enrichment.model_validate(response.enrichment.model_dump())
                        except Exception:
                            validation_failures += 1
                
                # Monitor peak memory usage
                current_resources = await self.system_monitor.get_current_resources()
                memory_peak_gb = min(memory_peak_gb, current_resources.memory_available_gb)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.debug(f"Batch failed during benchmark: {e}")
                continue
        
        actual_duration = time.time() - start_time
        
        # Calculate metrics
        throughput = successful_requests / actual_duration if actual_duration > 0 else 0
        
        # Latency percentiles
        if latencies:
            sorted_latencies = sorted(latencies)
            p50_latency = sorted_latencies[int(0.50 * len(sorted_latencies))]
            p95_latency = sorted_latencies[int(0.95 * len(sorted_latencies))]
            p99_latency = sorted_latencies[int(0.99 * len(sorted_latencies))]
        else:
            p50_latency = p95_latency = p99_latency = 0.0
        
        # Tokens per second
        avg_tokens_per_second = total_tokens / actual_duration if actual_duration > 0 else 0
        
        # Schema validation rate
        schema_validation_rate = 1.0 - (validation_failures / max(1, successful_requests))
        
        # Average confidence
        confidence_avg = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Peak memory usage (GB used = total - available)
        memory_total_gb = psutil.virtual_memory().total / (1024**3)
        memory_peak_used_gb = memory_total_gb - memory_peak_gb
        
        logger.info(
            f"Benchmark complete: {throughput:.1f} msg/s, "
            f"p95={p95_latency:.1f}ms, validation={schema_validation_rate:.2%}"
        )
        
        return ModelBenchmark(
            model_name=model_name,
            quantization=quantization,
            context_window=context_window,
            batch_size=batch_size,
            concurrent_requests=concurrent_requests,
            throughput_msgs_per_second=throughput,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            avg_tokens_per_second=avg_tokens_per_second,
            memory_peak_gb=memory_peak_used_gb,
            schema_validation_rate=schema_validation_rate,
            confidence_avg=confidence_avg,
            system_info=self.get_system_info(),
        )
    
    def _save_benchmark_result(self, benchmark: ModelBenchmark) -> None:
        """Save benchmark result to cache."""
        filename = (
            f"benchmark_{benchmark.model_name.replace(':', '_')}_"
            f"{benchmark.quantization}_"
            f"batch{benchmark.batch_size}_"
            f"concurrent{benchmark.concurrent_requests}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(asdict(benchmark), f, indent=2)
        
        logger.debug(f"Saved benchmark result: {filepath}")
    
    def load_cached_benchmarks(self) -> List[ModelBenchmark]:
        """Load previously cached benchmark results."""
        benchmarks = []
        
        for filepath in self.cache_dir.glob("benchmark_*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                    benchmark = ModelBenchmark(**data)
                    benchmarks.append(benchmark)
            except Exception as e:
                logger.warning(f"Failed to load benchmark {filepath}: {e}")
        
        return benchmarks
    
    def find_optimal_configuration(
        self,
        benchmarks: List[ModelBenchmark],
        prioritize: str = "throughput"  # "throughput", "latency", "balanced"
    ) -> Tuple[Optional[ModelBenchmark], List[OptimizationRecommendation]]:
        """Find optimal configuration and generate recommendations."""
        
        if not benchmarks:
            return None, []
        
        # Filter to NFR-compliant benchmarks
        nfr_compliant = [b for b in benchmarks if b.meets_nfr_targets]
        
        if not nfr_compliant:
            logger.warning("No benchmark configurations meet NFR targets")
            recommendations = self._generate_recommendations(benchmarks)
            return None, recommendations
        
        # Find optimal configuration based on priority
        if prioritize == "throughput":
            optimal = max(nfr_compliant, key=lambda b: b.throughput_msgs_per_second)
        elif prioritize == "latency":
            optimal = min(nfr_compliant, key=lambda b: b.p95_latency_ms)
        else:  # balanced
            # Weighted score: throughput (40%) + inverse latency (30%) + validation rate (30%)
            def balanced_score(b):
                normalized_throughput = min(b.throughput_msgs_per_second / 100.0, 1.0)
                normalized_latency = max(0, 1.0 - (b.p95_latency_ms / 500.0))
                normalized_validation = b.schema_validation_rate
                
                return (0.4 * normalized_throughput + 
                       0.3 * normalized_latency + 
                       0.3 * normalized_validation)
            
            optimal = max(nfr_compliant, key=balanced_score)
        
        recommendations = self._generate_recommendations(benchmarks)
        
        return optimal, recommendations
    
    def _generate_recommendations(self, benchmarks: List[ModelBenchmark]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on benchmark results."""
        recommendations = []
        
        if not benchmarks:
            return recommendations
        
        # Analyze patterns in benchmark results
        best_throughput = max(benchmarks, key=lambda b: b.throughput_msgs_per_second)
        best_latency = min(benchmarks, key=lambda b: b.p95_latency_ms)
        
        # Model recommendations
        if best_throughput.throughput_msgs_per_second < 25.0:
            recommendations.append(OptimizationRecommendation(
                category="model",
                recommendation="Consider switching to a smaller quantized model (Q4_K_S or 2B variant)",
                expected_improvement="30-50% throughput increase",
                priority="high",
                implementation_effort="easy"
            ))
        
        # System recommendations
        avg_memory_usage = sum(b.memory_peak_gb for b in benchmarks) / len(benchmarks)
        if avg_memory_usage > 12.0:  # High memory usage
            recommendations.append(OptimizationRecommendation(
                category="system",
                recommendation="Enable quantized KV cache and reduce context window",
                expected_improvement="20-40% memory reduction",
                priority="medium", 
                implementation_effort="easy"
            ))
        
        # Configuration recommendations
        high_latency_configs = [b for b in benchmarks if b.p95_latency_ms > 250.0]
        if len(high_latency_configs) > len(benchmarks) * 0.5:
            recommendations.append(OptimizationRecommendation(
                category="configuration",
                recommendation="Reduce concurrent requests and increase batch size",
                expected_improvement="15-25% latency reduction",
                priority="medium",
                implementation_effort="trivial"
            ))
        
        # Quality recommendations
        low_validation_configs = [b for b in benchmarks if b.schema_validation_rate < 0.95]
        if low_validation_configs:
            recommendations.append(OptimizationRecommendation(
                category="model",
                recommendation="Use higher quality quantization (Q5_K_M) for better schema compliance",
                expected_improvement="5-10% validation rate increase",
                priority="low",
                implementation_effort="easy"
            ))
        
        return recommendations


class AdaptiveOptimizer:
    """Real-time adaptive performance optimization."""
    
    def __init__(self, ollama_client, monitor_interval: float = 5.0):
        self.ollama_client = ollama_client
        self.monitor_interval = monitor_interval
        self.system_monitor = SystemMonitor()
        
        # Adaptive parameters
        self.min_concurrent = 1
        self.max_concurrent = 12
        self.min_batch_size = 1
        self.max_batch_size = 16
        
        # Performance tracking
        self.performance_history = []
        self.optimization_events = []
        
        self._monitoring = False
    
    async def start_adaptive_monitoring(self) -> None:
        """Start continuous adaptive optimization."""
        self._monitoring = True
        logger.info("Starting adaptive performance monitoring")
        
        while self._monitoring:
            try:
                await self._optimization_cycle()
                await asyncio.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Adaptive optimization error: {e}")
                await asyncio.sleep(self.monitor_interval)
    
    def stop_adaptive_monitoring(self) -> None:
        """Stop adaptive monitoring."""
        self._monitoring = False
        logger.info("Stopped adaptive performance monitoring")
    
    async def _optimization_cycle(self) -> None:
        """Single optimization cycle."""
        # Get current system resources
        resources = await self.system_monitor.get_current_resources()
        
        # Get current performance metrics
        perf_metrics = self.ollama_client.get_performance_metrics()
        
        # Record current state
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "throughput": perf_metrics.get("throughput_requests_per_second", 0),
            "p95_latency": perf_metrics.get("p95_latency_ms", 0),
            "memory_percent": resources.memory_percent,
            "cpu_percent": resources.cpu_percent,
            "concurrent_requests": self.ollama_client.max_concurrent,
        })
        
        # Keep only recent history (last 20 samples)
        if len(self.performance_history) > 20:
            self.performance_history = self.performance_history[-20:]
        
        # Apply adaptive optimizations
        optimizations_applied = []
        
        # Memory-based optimization
        if resources.is_memory_constrained:
            if self.ollama_client.max_concurrent > self.min_concurrent:
                self.ollama_client.max_concurrent = max(
                    self.min_concurrent,
                    self.ollama_client.max_concurrent - 1
                )
                optimizations_applied.append("reduced_concurrent_requests")
        
        # CPU-based optimization
        elif resources.cpu_percent < 50.0:  # CPU underutilized
            if self.ollama_client.max_concurrent < self.max_concurrent:
                self.ollama_client.max_concurrent = min(
                    self.max_concurrent,
                    self.ollama_client.max_concurrent + 1
                )
                optimizations_applied.append("increased_concurrent_requests")
        
        # Throughput-based optimization
        current_throughput = perf_metrics.get("throughput_requests_per_second", 0)
        if len(self.performance_history) >= 3:
            # Check if throughput is declining
            recent_throughputs = [h["throughput"] for h in self.performance_history[-3:]]
            if all(recent_throughputs[i] > recent_throughputs[i+1] for i in range(len(recent_throughputs)-1)):
                # Throughput is declining, reduce concurrency
                if self.ollama_client.max_concurrent > self.min_concurrent:
                    self.ollama_client.max_concurrent -= 1
                    optimizations_applied.append("throughput_based_reduction")
        
        # Log optimizations
        if optimizations_applied:
            optimization_event = {
                "timestamp": datetime.now().isoformat(),
                "optimizations": optimizations_applied,
                "new_concurrent": self.ollama_client.max_concurrent,
                "system_state": {
                    "memory_percent": resources.memory_percent,
                    "cpu_percent": resources.cpu_percent,
                    "throughput": current_throughput,
                }
            }
            
            self.optimization_events.append(optimization_event)
            
            logger.info(
                f"Applied optimizations: {optimizations_applied}, "
                f"new concurrent requests: {self.ollama_client.max_concurrent}"
            )
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get detailed optimization report."""
        return {
            "monitoring_active": self._monitoring,
            "current_config": {
                "max_concurrent": self.ollama_client.max_concurrent,
                "model_name": self.ollama_client.model_config.name,
            },
            "performance_history": self.performance_history,
            "optimization_events": self.optimization_events,
            "summary": {
                "total_optimizations": len(self.optimization_events),
                "avg_throughput": sum(h["throughput"] for h in self.performance_history) / max(1, len(self.performance_history)),
            }
        }