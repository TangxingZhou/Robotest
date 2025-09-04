from .controller import *
from .models import *

@allure.step('等待导出任务完成')
def wait_export_task_completes(task_name, connector_name, export_files, _export_controller: ExportController, _timeout=300):
    tasks, total = _export_controller.get_task_list(
        name=task_name,
        status=ExportTaskStatus.Completed,
        _timeout=_timeout,
        _interval=5,
        expected_condition=lambda x: len(x) > 0
    )
    assert len(tasks) > 0, f"export task '{task_name}' was not complete successfully"
    task =  tasks[0]
    task.fields_are_correct(
        task_name,
        [[f['target_volume_name'], f['target_volume_branch'], f['name']] for f in export_files],
        connector_name
    )
    task.is_completed()
    task.is_to_mo()
    return tasks[0]

@allure.step('查看导出任务详情')
def check_export_task_details(
        task_id,
        task_name,
        connector_name,
        connector_type,
        merge_title_to_text,
        _export_controller: ExportController,
        **kwargs
):
    task_info = _export_controller.get_task_info(task_id)
    task_info.fields_are_correct(task_id, task_name, connector_name, _export_controller.user_name, merge_title_to_text)
    task_info.is_completed()
    task_info.is_to_mo()
    task_info.config_is_correct(ExportConfig(f'{connector_type}_config', **kwargs))

@allure.step('查看导出任务的文件详情')
def check_files_of_export_task(task_id, export_files, _export_controller: ExportController):
    task_files, total = _export_controller.get_task_files(task_id)
    assert total == len(export_files), f"expected {len(export_files)} files, but got {total}"
    sorted_files = sorted(task_files, key=lambda f: f.full_path[2])
    for index, name in enumerate(sorted(export_files, key=lambda f: f['name'])):
        file = sorted_files[index]
        file.fields_are_correct([name['target_volume_name'], name['target_volume_branch'], name['name']])
        file.is_completed()

@allure.step('删除导出任务成功')
def delete_export_task(task_id, _export_controller: ExportController):
    _export_controller.delete_task(task_id)
    tasks, _ = _export_controller.get_task_list()
    assert task_id not in [t.id for t in tasks], f"export task '{task_id}' was not deleted successfully"
