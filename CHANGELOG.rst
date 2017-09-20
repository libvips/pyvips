# master 

## Version 2.0.5 (8 September 2017)

* minor polish

## Version 2.0.4 (3 September 2017)

* clear error log after failed get_typeof in get() workaround
* more tests pass with older libvips
* fix typo in logging handler

## Version 2.0.3 (2 September 2017)

* fix get() with old libvips
* better collapse for docs [kleisauke]
* add `get_fields()`

## Version 2.0.2 (26 August 2017)

* support `pyvips.__version__`
* add `version()` to get libvips version number
* add `cache_set_max()`, `cache_set_max_mem()`, `cache_set_max_files()`, 
  `cache_set_trace()`
* all glib log levels sent to py logger
* docs are collapsed for less scrolling [kleisauke]

## Version 2.0.1 (23 August 2017)

* doc revisions
* fix test suite on Windows
* redirect libvips warnings to logging
* fix debug logging

## Version 2.0.0 (19 August 2017)

* rewrite on top of 'cffi' 
