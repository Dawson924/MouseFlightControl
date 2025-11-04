#include <stdint.h>

#ifdef _WIN32
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

int32_t vjoy(int32_t val, int32_t min, int32_t max) {
    if (val < min) val = min;
    else if (val > max) val = max;

    double ratio = (double)(val - min) / (max - min);
    return (int32_t)(ratio * 32767) + 1;
}