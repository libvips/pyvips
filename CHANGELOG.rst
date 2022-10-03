# master 

+ fix with libvips nodeprecated [kleisauke]
+ update README notes for py3.8+ on win [CristiFati]

## Version 2.2.1 (released 12 Jun 2022)

* add seek and end handlers for TargetCustom [jcupitt]
* add `block_untrusted_set`, `operation_block_set` [jcupitt]
* update for libvips 8.13 [jcupitt]
 
## Version 2.2.0 (released 18 Apr 2022)

* `repr()` will print matrix images as matrices [jcupitt]
* more robust bandwise index/slice; added fancy slicing (step != 1) [erdmann]
* fix `im.bandjoin([])`, now returns `im` [erdmann]
* add numpy-style extended indexing (index with list of ints or bools) [erdmann]
* earlier detection of unknown methods and class methods [jcupitt]
* add conversion from Image to numpy array via 'Image.__array__` [erdmann]
* add `Image.fromarray()` for conversion from numpy-ish arrays [erdmann]
* add `invalidate()` [jcupitt]
* add array-like functionality to `Image.new_from_array()` for conversion from
  numpy-ish arrays [erdmann]
* add `Image.numpy()` (convenient for method chaining) [erdmann]
* add `tolist()` [erdmann]
* accept `pathlib.Path` objects for filenames (py3 only) [erdmann]
* cache pspec lookups for a 10% speed boost [jcupitt]

## Version 2.1.16 (started 28 Jun 2021)

* fix logging of deprecated args [manthey]
* add shepards example [tourtiere]
* update docs for 8.12 [jcupitt]
* add pagesplit(), pagejoin(), get_page_height(), get_n_pages() [jcupitt]
* add atan2() [jcupitt]
* add `cache_get_max()`, `cache_get_max_mem()`, `cache_get_max_files()`, 
  `cache_get_size()` [hroskes]
* don't generate docs for deprecated arguments [jcupitt]
* buffer save tries with the target API first [jcupitt]
* add hyperbolic functions `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, 
  `atanh` [jcupitt]
* add `values_for_flag` [kleisauke]

## Version 2.1.15 (27 Dec 2020)

* better autodocs for enums [int-ua]
* better unreffing if operators fail [kleisauke]

## Version 2.1.14 (18 Dec 2020)

* add `stdio.py` example
* update examples
* improve formatting of enum documentation
* regenerate docs
* remove old `vips_free` declaration, fixing API build on some platforms 
  [rajasagashe]

## Version 2.1.13 (4 Jul 2020)

* better diagnostics for API mode install failure [kleisauke]
* revise docs [int-ua]
* better reference tracking for new_from_memory [aspadm]

## Version 2.1.12 (17 Feb 2020) 

* update enums.py [tony612]
* add gen-enums.py [jcupitt]
* improve custom source/target types [jcupitt]
* revise types for set_blob to fix exception with old libvips [jcupitt]
* fix 32-bit support [dqxpb]
* remove pytest-runner from pipy deps [lgbaldoni]
* add watermark with image example [jcupitt]

## Version 2.1.11 (7 Nov 2019) 

* revise README [jcupitt]
* add watermark example [jcupitt]
* fix syntax highlighting in README [favorable-mutation]
* add signal handling [jcupitt]
* add Source / Target support [jcupitt]
* add perf tests [kleisauke]
* speed up Operation.call [kleisauke]
* fix logging [h4l]

## Version 2.1.8 (1 Jul 2019)

* fix regression with py27 [jcupitt]

## Version 2.1.7 (1 Jul 2019)

* prevent exponential growth of reference tables in some cases [NextGuido]

## Version 2.1.6 (7 Jan 2019)

* switch to new-style callbacks [kleisauke]
* add get_suffixes() [jcupitt]
* add Region [jcupitt]
* better handling of NULL strings from ffi [jcupitt]
* add support for dealing with uint64 types [kleisauke]

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
