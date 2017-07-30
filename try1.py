#!/usr/bin/env python

import Vips

print 'test gvalue bool'
gv = Vips.GValue()
gv.init(Vips.GValue.gbool_type)
gv.set(True)
value = gv.get()
print 'gvalue =', value
gv.set(False)
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue int'
gv = Vips.GValue()
gv.init(Vips.GValue.gint_type)
gv.set(12)
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue double'
gv = Vips.GValue()
gv.init(Vips.GValue.gdouble_type)
gv.set(3.1415)
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue enum'
Vips.vips_lib.vips_interpretation_get_type()
interpretation_gtype = Vips.gobject_lib.g_type_from_name('VipsInterpretation')
print 'interpretation_gtype =', interpretation_gtype
gv = Vips.GValue()
gv.init(interpretation_gtype)
gv.set("xyz")
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue flags'
Vips.vips_lib.vips_operation_flags_get_type()
operationflags_gtype = Vips.gobject_lib.g_type_from_name('VipsOperationFlags')
print 'operationflags_gtype =', operationflags_gtype
gv = Vips.GValue()
gv.init(operationflags_gtype)
gv.set(12)
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue str'
gv = Vips.GValue()
gv.init(Vips.GValue.gstr_type)
gv.set("banana")
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue array int'
gv = Vips.GValue()
gv.init(Vips.GValue.array_int_type)
gv.set([1, 2, 3])
value = gv.get()
print 'gvalue =', value
print ''

print 'test gvalue array double'
gv = Vips.GValue()
gv.init(Vips.GValue.array_double_type)
gv.set([1.1, 2.2, 3.3])
value = gv.get()
print 'gvalue =', value
print ''


