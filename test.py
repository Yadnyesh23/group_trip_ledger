list1 = [1,2,3]
expense_amount = 1000
total_participants=len(list1)

per_person = expense_amount / total_participants
allocation = {}

for p in list1:
    allocation[p] = per_person

print(allocation)


# custom_allocations = {
#     1 : 200,
#     2 : 400,
#     3 : 200
# }

# expense_amount = 1000

# custom_allocation = 0
# for value in custom_allocations.values():
#     custom_allocation += value
# print(custom_allocation)

