# master 

## Version 2.1.6 (7 Jan 2019)

* switch to new-style callbacks [kleisauke]
* add get_suffixes() [jcupitt]

## Version 2.1.5 (18 Dec 2018)

* better behaviour for new_from_memory fixes some segvs [wppd]
* added addalpha/hasalpha [jcupitt]

## Version 2.1.4 (3 Oct 2018)

* update links for repo move [jcupitt]
* update autodocs for libvips 8.7 [jcupitt]

## Version 2.1.3 (3 March 2018)

* record header version number in binary module and check compatibility with
  the library during startup [jcupitt]
* add optional output params to docs [kleisauke]
* update docs [jcupitt]
* add some libvips 8.7 tests [jcupitt]
* move to pytest [kleisauke]
* better handling of many-byte values in py3 new_from_memory [MatthiasKohl]
* better handling of utf-8 i18n text [felixbuenemann]
* add enum introspection [kleisauke]
* move the libvips test suite back to libvips, just test pyvips here [jcupitt]
* fix five small memleaks [kleisauke]

## Version 2.1.2 (1 March 2018)

* only use get_fields on libvips 8.5+ [rebkwok]
* only use parent_instance on libvips 8.4+ [rebkwok]
* relative import for decl 

## Version 2.1.1 (25 February 2018)

* switch to sdist
* better ABI mode fallback behaviour

## Version 2.1.0 (17 November 2017)

* support cffi API mode as well: much faster startup, about 20% faster on the 
  test suite [jcupitt]
* on install, it tries to build a binary interface, and if that fails, falls 
  back to ABI mode [jcupitt]
* better error for bad kwarg [geniass]

## Version 2.0.6 (22 February 2017)

* add version numbers to library names on linux

## Version 2.0.5 (8 September 2017)

* minor polish
* more tests
* add `composite` convenience method
* move tests outside module [greut]
* switch to tox [greut]
* allow info message logging

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
