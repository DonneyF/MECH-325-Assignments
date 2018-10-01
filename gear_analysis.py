from gears import Gear

gears = Gear()

bending_stress = gears.bending_stress("5172T21", "2272839", None, None, 2)
safety_factor_bending = gears.safety_factor_bending("2272839", bending_stress)

contact_stress = gears.contact_stress("5172T21", "2272839", None, None, 2)
safety_factor_contact = gears.safety_factor_contact("5172T21", "2272839", contact_stress)

cost = gears.interaction_cost("5172T21", "2272839")
print("=======================")
print("Example Calculation:")
print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\nCost: {}"
      .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact,cost))
print("tangential force: {}\n".format(gears.tangential_force(gears.get("5172T21"), gears.get("2272839"), None, None)))
print("=======================")
gears_0 = Gear()

bending_stress = gears_0.bending_stress("5172T21", "5172T25", None, None, 2)
safety_factor_bending = gears_0.safety_factor_bending("5172T25", bending_stress)

contact_stress = gears_0.contact_stress("5172T21", "5172T25", None, None, 2)
safety_factor_contact = gears_0.safety_factor_contact("5172T21", "5172T25", contact_stress)

cost = gears_0.interaction_cost("5172T21", "5172T25")

print("16:80")
print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\nCost: {}"
      .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact,cost))
print("tangential force: {}\n".format(gears.tangential_force(gears.get("5172T21"), gears.get("5172T25"), None, None)))
print("=======================")
gears_1 = Gear()

bending_stress = gears_1.bending_stress("7880K26", "6832K58", None, None, 2)
safety_factor_bending = gears_1.safety_factor_bending("7880K26", bending_stress)

contact_stress = gears_1.contact_stress("7880K26", "6832K58", None, None, 2)
safety_factor_contact = gears_1.safety_factor_contact("7880K26", "6832K58", contact_stress)

cost = gears_1.interaction_cost("7880K26", "6832K58")

print("14:72")
print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\nCost: {}"
      .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact,cost))
print("tangential force: {}\n".format(gears.tangential_force(gears.get("7880K26"), gears.get("6832K58"), None, None)))
print("=======================")
gears_2 = Gear()

bending_stress = gears_2.bending_stress("7880K37", "6832K66", None, None, 2)
safety_factor_bending = gears_2.safety_factor_bending("7880K37", bending_stress)

contact_stress = gears_2.contact_stress("7880K37", "6832K66", None, None, 2)
safety_factor_contact = gears_2.safety_factor_contact("7880K37", "6832K66", contact_stress)

cost = gears_2.interaction_cost("7880K37", "6832K66")

print("12:60")
print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\nCost: {}"
      .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact,cost))
print("tangential force: {}\n".format(gears.tangential_force(gears.get("7880K37"), gears.get("6832K66"), None, None)))
