from typing import Any, Dict, List

import psutil


class FlightSimApps:
    def __init__(self, process_names: List[str]) -> None:
        self.process_names = [name.lower() for name in process_names]
        self.process_info: Dict[str, Dict[str, Any]] = {}
        self._detect_processes()

    def _detect_processes(self) -> None:
        all_processes = list(psutil.process_iter(['pid', 'name', 'exe', 'status', 'cpu_percent', 'memory_info']))
        for target_name in self.process_names:
            process_data = {'available': False, 'instances': []}
            for proc in all_processes:
                try:
                    if proc.info['name'] and proc.info['name'].lower() == target_name:
                        process_data['available'] = True
                        process_data['instances'].append(
                            {
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'exe': proc.info['exe'],
                                'status': proc.info['status'],
                                'cpu_percent': proc.info['cpu_percent'],
                                'memory_rss': proc.info['memory_info'].rss if proc.info['memory_info'] else 0,
                                'memory_vms': proc.info['memory_info'].vms if proc.info['memory_info'] else 0,
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            self.process_info[target_name] = process_data

    def refresh(self) -> None:
        self.process_info.clear()
        self._detect_processes()

    def process(self, process_name: str) -> Dict[str, Any]:
        lower_name = process_name.lower()
        return self.process_info.get(lower_name, {'available': False, 'instances': []})

    def dump(self) -> Dict[str, Dict[str, Any]]:
        return self.process_info.copy()


if __name__ == '__main__':
    app_instances = FlightSimApps(['Steam.exe'])
    print(app_instances.dump())
