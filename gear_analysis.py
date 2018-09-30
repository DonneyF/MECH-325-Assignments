from gears import Gear

gears = Gear()

bending_stress = gears.bending_stress("5172T21", "2272839", None, None, 2)
safety_factor_bending = gears.safety_factor_bending("2272839", bending_stress)

contact_stress = gears.contact_stress("5172T21", "2272839", None, None, 2)
safety_factor_contact = gears.safety_factor_contact("5172T21", "2272839", contact_stress)

print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}"
      .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact))
