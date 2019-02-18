
#creates a blank grid for the megabox
# python blank_grid_gen.py > grid,csv

print("box_number,user_id,home_digit,vstr_digit")
i = 1
while i <= 100:
	s = "%d,None,," % i
	print(s)
	i += 1