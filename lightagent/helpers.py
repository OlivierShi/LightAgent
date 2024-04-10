

class Helpers:
    @staticmethod
    def metrics_helper(metrics: dict, metric_name: str, segment_name: str, metric_value: float) -> None:
        if metric_name not in metrics:
            metrics[metric_name] = {}
        
        if segment_name not in metrics[metric_name]:
            metrics[metric_name][segment_name] = []
        
        metrics[metric_name][segment_name].append(metric_value)

    @staticmethod
    def metrics_printer(metrics: dict):
        for metric_name, segments in metrics.items():
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
                print(f"\tSegment: {segment_name}")
                print(f"\t\tAverage: {sum(values) / len(values)}")
                print(f"\t\tCount: {len(values)}")
            print(f"\tReasoning total: {reasoning_perf}\tReasoning avg: {reasoning_perf/reasoning_cnt}\n\tResponding total: {responding_perf}\n\tTool Executions: {executions}\n")