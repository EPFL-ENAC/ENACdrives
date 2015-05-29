from config import models as mo

obj_tier1 = mo.Config.objects.get(name="NAS2 Tier1")
obj_tier2 = mo.Config.objects.get(name="NAS2 Tier2")
obj_tier4 = mo.Config.objects.get(name="NAS2 Tier4")

units_tier1 = """
acm, alice, aphys, aprl, archizoom, cclab, cdt-enac, ceat, cnpa, cryos, disal,
east-co, echo, ecol, ecos, eesd, eflum, eml, enac-do, enac-it, enac-oc, form, 
gis-ge, gr-cel, gr-gn, gr-lud, gr-per, gr-tz, ia-ge, ibeton, ibois, icom, 
iic-ge, iie-ge, imac, inter-ge, lab-u, laba, labex, labex-co, lac, lamu, lapis,
lasig, last, lasur, laure, lavoc, lbe, lcc, lce, lch, leso-pb, leure, lgb, lhe,
lipid, liv, lmce, lmr, lms, lsms, lte, lth2, lth3, ltqe, luts, manslab-co, mcs, 
reme, sgc-ge, ssie-ge, sub, topo, tox, transp-or, tsam, wire"""

units_tier2 = """
acm, alice, aphys, aprl, archizoom, cclab, cdt-enac, ceat, cnpa, cryos, disal,
east-co, echo, ecol, ecos, eesd, eflum, eml, enac-do, enac-it, enac-oc, form, 
gis-ge, gr-cel, gr-gn, gr-lud, gr-per, gr-tz, ia-ge, ibeton, ibois, icom, 
iic-ge, iie-ge, imac, inter-ge, lab-u, laba, labex, labex-co, lac, lamu, lapis,
lasig, last, lasur, laure, lavoc, lbe, lcc, lce, lch, leso-pb, leure, lgb, lhe,
lipid, liv, lmce, lmr, lms, lsms, lte, lth2, lth3, ltqe, luts, manslab-co, mcs, 
reme, sgc-ge, ssie-ge, sub, topo, tox, transp-or, tsam, wire"""

units_tier4 = "ibeton"

units_tier1 = [u.strip() for u in units_tier1.split(",")]
units_tier2 = [u.strip() for u in units_tier2.split(",")]
units_tier4 = [u.strip() for u in units_tier4.split(",")]


# Feed units for NAS2 Tier1
obj_tier1.epfl_units.clear()
for u in units_tier1:
    obj_u = mo.EpflUnit.objects.get_or_create(name=u)[0]
    obj_tier1.epfl_units.add(obj_u)

# Feed units for NAS2 Tier2
obj_tier2.epfl_units.clear()
for u in units_tier2:
    obj_u = mo.EpflUnit.objects.get_or_create(name=u)[0]
    obj_tier2.epfl_units.add(obj_u)

# Feed units for NAS2 Tier4
obj_tier4.epfl_units.clear()
for u in units_tier4:
    obj_u = mo.EpflUnit.objects.get_or_create(name=u)[0]
    obj_tier4.epfl_units.add(obj_u)

obj_tier1.save()
obj_tier2.save()
obj_tier4.save()
