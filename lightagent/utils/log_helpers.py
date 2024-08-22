import io

class LogHelpers:
    @staticmethod
    def metrics_helper(metrics: dict, metric_name: str, segment_name: str, metric_value: float) -> None:
        if metric_name not in metrics:
            metrics[metric_name] = {}
        
        if segment_name not in metrics[metric_name]:
            metrics[metric_name][segment_name] = []
        
        metrics[metric_name][segment_name].append(metric_value)

    @staticmethod
    def metrics_log_helper(metrics: dict, metric_name: str, log: str, duration: float = None) -> None:
        if metric_name not in metrics:
            metrics[metric_name] = []
        
        if duration is not None:
            log += f"\n[Duration: {duration} s]"

        metrics[metric_name].append(log)

    @staticmethod
    def metrics_printer(metrics: dict):
        for metric_name, segments in metrics.items():
            if metric_name == "perf":
                print(f"Metric: {metric_name}")
                reasoning_perf = 0.0
                reasoning_cnt = 0
                responding_perf = 0.0
                executions = 0.0
                for segment_name, values in segments.items():
                    if segment_name == "respond":
                        responding_perf = values[0]
                    elif segment_name == "execute_function":
                        executions += sum(values)
                    else:
                        reasoning_perf += sum(values)
                        reasoning_cnt += len(values)
                print(f"\tReasoning total: {reasoning_perf}\tResponding total: {responding_perf}")
            
            if metric_name == "log":
                print(f"Metric: {metric_name}")
                for l in segments:
                    print(f"\t{l}")

    @staticmethod
    def details_logger(metrics: dict, logger_path: str):
        with open(logger_path, 'w', encoding='utf-8') as logger:
            logger.write("\n".join(metrics["details"]))
            logger.write("\n")
