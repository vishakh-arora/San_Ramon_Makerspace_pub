import barcode
import mail
from barcode.writer import ImageWriter

# Read all orders
fin = open("orders.txt","r")
orders_list = fin.read().split("\n")
#print(orders_list)

# Parse orders
orders = {}
for i in range(len(orders_list)):
    order = orders_list[i].split(";")
    orders[order[0]] = []
    for j in range(1,len(order)):
        orders[order[0]].append(order[j])

# Generate
EAN = barcode.get_barcode_class('ean8')
for y in orders.keys():
    if len(y) > 0:
        orderID = str(y)
        ean = EAN(y, writer=ImageWriter())
        fullname = ean.save('order_' + str(y))
#print("Enter email")
# Send email with bar code
        email = "vishakh.arora29@gmail.com"
        mail.mail( email, "Thank you for your Lunch order", "Your lunch order ID " +orderID+" has been placed.", "order_" + orderID + ".png")


while (True):
    print("Enter order number")
    order_num = input()
    # Remove last digit
    order_num = order_num[0:len(order_num)-1]

    h=orders.get(order_num)
    if (h != None):
        print("\nStudent with order number "+ order_num +" ordered ")
        for j in range(len(h)):
            print(str(j+1) + "\t" + h[j])
    print("\n\n")

