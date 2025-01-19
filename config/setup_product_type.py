DEVICE_TYPE_DEPENDENCY = {'pad': 'tablet',
                          'tab': 'tablet',
                          'tablet': 'tablet',
                          'laptop': 'laptop',
                          'phone': 'phone',
                          'watch': 'watch'
                          }


async def detect_device_type(url: str) -> str:
    for k in DEVICE_TYPE_DEPENDENCY.keys():
        if k in url:
            return DEVICE_TYPE_DEPENDENCY[k]
    return 'phone'
