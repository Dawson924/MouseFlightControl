#include <Python.h>
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
        return NULL;
    }
    double ratio = (double)(val - AXIS_MIN) / (AXIS_MAX - AXIS_MIN);
    int32_t result = (int32_t)(ratio * 32767) + 1;
    return PyLong_FromLong(result);
}

static PyMethodDef CalcMethods[] = {
    {
        "map_to_vjoy",
        calc_map_to_vjoy,
        METH_VARARGS,
        "Map value to vJoy axis range (1-32768)"
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef calcmodule = {
    PyModuleDef_HEAD_INIT,
    "calc",
    "A C extension module for calculations",
    -1,
    CalcMethods
};

PyMODINIT_FUNC PyInit_calc(void) {
    return PyModule_Create(&calcmodule);
}
