#include <Python.h>  // Python C API头文件
#include <stdint.h>

#define AXIS_MIN (-32767)
#define AXIS_MAX 32767

/**
 * 将输入值映射到vJoy设备的轴范围（1-32768）
 * 对应Python函数：map_to_vjoy(val)
 */
static PyObject* calc_map_to_vjoy(PyObject* self, PyObject* args) {
    int32_t val;
    if (!PyArg_ParseTuple(args, "i", &val)) {
        return NULL;  // 参数解析失败返回NULL
    }
    double ratio = (double)(val - AXIS_MIN) / (AXIS_MAX - AXIS_MIN);
    int32_t result = (int32_t)(ratio * 32767) + 1;
    return PyLong_FromLong(result);
}

// 方法列表：定义模块中的函数
static PyMethodDef CalcMethods[] = {
    {
        "map_to_vjoy",
        calc_map_to_vjoy,
        METH_VARARGS,
        "Map value to vJoy axis range (1-32768)"
    },
    {NULL, NULL, 0, NULL}  // 终止符
};

// 模块定义
static struct PyModuleDef calcmodule = {
    PyModuleDef_HEAD_INIT,
    "calc",
    "A C extension module for calculations",
    -1,
    CalcMethods
};

// 模块初始化函数
PyMODINIT_FUNC PyInit_calc(void) {
    return PyModule_Create(&calcmodule);
}
