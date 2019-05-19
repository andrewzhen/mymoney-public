import glob
import sys
import pandas as pd

ea_types = ["Food","Education","Utilities","Personal","Transportation","Sky","Assets"]
colors = ["\033[38;5;1m", "\033[38;5;207m", "\033[38;5;250m", \
"\033[38;5;208m", "\033[38;5;2m", "\033[38;5;42m", "\033[38;5;240m"]
days = range(0,32)
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
row_length = 4


# Requests user for action
def menu(action):
  global file_name

  # Valid options
  v = ["View", "view", "V", "v"]
  a = ["Add", "add", "A", "a"]
  u = ["Update", "update", "U", "u"]
  d = ["Delete", "delete", "D", "d"]
  r = ["Return", "return", "R", "r"]
  
  # Read file
  contents = fileToList(file_name)
  
  if action in v:
    view(file_name)
    return False
  elif action in r:
    file_name = select_file("*EA.csv")
    return False
  elif action in a + u + d:
    # Get info
    if action in a:
      invalid = True
      while invalid:
        date = validInput(input("\nDate [dd-mmm]: ").title(), "date")
        description = validInput(input("Description: ").title(), "description")
        # Prevent duplicates
        for ele in range(len(contents)):
          if date == contents[ele] and description == contents[ele + 1]:
            print("\nThis date and description already exists")
            break
          elif ele == len(contents) - 1:
            invalid = False
      add(date, description)
      return False
    else:
      date = validInput(input("\nDate [dd-mmm]: ").title(), "Date", contents)
      description = validInput(input("Description: ").title(), "Description", contents)
      if action in u:
        update(date, description, contents)
        return False
      else:
        delete(date, description)
        return False
  else:
    print("\nExited")
    return True


# Select file
def select_file(pattern):
  print("\nSelect file:\n")
  files = glob.glob(pattern)
  for file in range(len(files)):
    print(str(file + 1) + ") " + files[file])
  return files[validInput(input("\n>>> "), "File", files)]


# Adds a new item to list and prints it
def add(when, what, how_much = 0, type_of = ""):
  date_len = 2
  stats_len = 136

  # Retrieve input and verifies
  if not how_much and not type_of:
    how_much = validInput(input("Value [$]: "), "Value")
    type_of = validInput(input("Type {0}: ".format(ea_types)), "Type")
  how_much = "${:.2f}".format(float(how_much.replace('$','').replace(',','')))

  # Retrieve proper type
  type_of = [cat for cat in ea_types if cat[0].upper() == type_of[0].upper()][0]
  
  # Read file
  contents = fileToList(file_name)
  
  # Overwrite file
  file = open(file_name, 'w')
  copy_contents = contents[:]
  content_len = len(contents)
  for cell in range(0, content_len, 4):
    if len(str(copy_contents[cell]).split('-')) == date_len:

      # Split dates
      month = months.index(copy_contents[cell].split('-')[1]) + 1
      day = int(copy_contents[cell].split('-')[0])
      input_month = months.index(when.split('-')[1].title()) + 1
      input_day = int(when.split('-')[0])

      # Add by date
      chronological = (input_month < month) or (input_month == month and input_day <= day) or \
        cell == len(copy_contents) - stats_len

      if chronological:
        if cell == len(copy_contents) - stats_len:
          add_index = [4,5,6,7]
        else:
          add_index = [0,1,2,3]

        contents.insert(cell + add_index[0], when)
        contents.insert(cell + add_index[1], what)
        contents.insert(cell + add_index[2], how_much)
        contents.insert(cell + add_index[3], type_of)
        break

  # Calculate stats  
  content_len = len(contents)
  cat_sum = getSum(contents, content_len - stats_len + 4)
  for cell in range(content_len - stats_len + 5, content_len, row_length):
    if str(contents[cell]) != 'nan':
      contents[cell + 1] = cat_sum[0].replace(',','')
      del cat_sum[0]
  
  # Write to file
  new_file = listToCSV(contents)
  file.write(new_file)
  file.close()

  # Prints an item's details after adding
  print("\nSuccessfully added:\n" + "".join(when.ljust(9)) + \
        "".join(what.ljust(26)) + "".join(how_much.ljust(12)) + \
        getColor(type_of) + "\n")


# Update
def update(date, description, contents):
  # Instructions
  print("\nSelect those to update: Date(1), Description(2), Value(3), Type(4)")
  print("Ex. \"12\" would update Date and Description")

  # Verify valid number
  toUpdate = ""
  while type(toUpdate) != int and len(str(toUpdate)) <= row_length:
    try:
      toUpdate = int(input("\nEnter a number: "))
    except ValueError:
      print("Invalid input")

  # Parse user's input
  user = []
  for selection in range(len(str(toUpdate))):
    user.append(toUpdate % 10)
    toUpdate = round(toUpdate / 10)
  user.sort()
  
  # Requests for updated information
  new_data = []
  selection = [" ", "date", "description", "Value", "Type"]
  print("")
  for pick in user:
    user_input = validInput(input("Enter the updated " + selection[pick] + \
                                  ": ").title(),selection[pick],contents)
    new_data.append(user_input)

  # Get updated contents
  toPrint = ""
  copy_contents = contents[:]
  for cell in range(len(contents)):
    if contents[cell] == date and contents[cell + 1] == description:
      for counter in user:
        copy_contents[cell + counter - 1] = new_data[0]
        del new_data[0]
      toPrint = copy_contents[cell:cell + row_length]
      break

  delete(date, description)
  add(toPrint[0], toPrint[1], toPrint[2], toPrint[3])


# Delete
def delete(date, description):
  # Read file and parse into list
  file = open(file_name, 'r')
  parsed_file = file.read().replace('\n', ',').split(',')
  copy_file = parsed_file[:]
  file.close()
  
  # Delete item matching input
  deleted_cells = ""
  for cell in range(len(copy_file)):
    if copy_file[cell] == date and copy_file[cell + 1] == description:
      deleted_cells = copy_file[cell:cell + row_length]
      parsed_file = parsed_file[:cell] + parsed_file[cell + row_length:]

  # Convert list to csv
  new_file = listToCSV(parsed_file)

  # Write to file
  file = open(file_name, 'w')
  file.write(new_file)
  file.close()
  
  # Prints an item's details after deleting
  if deleted_cells:
    print("\nSuccessfully deleted:\n" + \
          "".join(deleted_cells[0].ljust(9)) + \
          "".join(deleted_cells[1].ljust(26)) + \
          "".join(deleted_cells[2].ljust(12)) + \
          getColor(deleted_cells[3]) + "\n")
  else:
    print("\nNo items match the date and description\n")


# View
def view(file_name):
  contents = fileToList(file_name)
  length = getLength(contents)

  # Items
  print("")
  for item in range(0, len(contents) - 132, row_length):
    day = int(contents[item].split('-')[0])
    month = contents[item].split('-')[1]
    if month in ["Jul","Aug"] or month == "Jun" and day > 15 or month == "Sep" and day < 28:
      print(getLight("".join(contents[item].ljust(8) + " ") + 
                     "".join(contents[item + 1].ljust(25) + " ") + 
                     "".join(str(contents[item + 2]).replace(',','').ljust(11)),0,0),
      getColor(contents[item + 3]))
    else:
      print("".join(contents[item].ljust(8)),
            "".join(contents[item + 1].ljust(25)),
            "".join(str(contents[item + 2]).replace(',','').ljust(11)),
            getColor(contents[item + 3]))

  # Stats
  cat_sum = getSum(contents, length)
  print("")
  section = 0
  for item in range(len(contents) - 128, len(contents), 4):
    if str(contents[item + 1]) != 'nan':
      print("".ljust(8), getLight(contents[item + 1], item, length), 
            "".join(cat_sum[section].replace(',','').ljust(11)))
      section += 1
    else:
      print("")
  print("")


# Returns the sum of each category
def getSum(contents, length):
  formatLen = [1, 8, 9, 14, 15, 29, 30, 33] # stats spacing

  sums = []
  for start in range(0, len(formatLen), 2):
    # Category
    if start == 0:
      cat_sum = [0] * len(ea_types)  
      for item in range(3, length, 4):
        cat_sum[ea_types.index(contents[item])] += float(contents[item - 1].replace('$','').replace(',',''))
      cat_sum[4] += cat_sum[5] # Transportation includes Sky

    # Quarter
    elif start == 2:
      cat_sum = [0] * 5
      for item in range(0, length - 3, 4):
        day = int(contents[item].split('-')[0])
        month = months.index(contents[item].split('-')[1]) + 1

        if contents[item + 3] != "Assets":
          # Fall
          if (month > 9 and month < 12) or (month == 9 and day >= 27) or (month == 12 and day <= 15):
            cat_sum[0] += float(contents[item + 2].replace('$',''))
          # Winter Break
          elif (month == 12 and day >= 16) or (month == 1 and day <= 6):
            cat_sum[1] += float(contents[item + 2].replace('$',''))
          # Winter
          elif (month > 1 and month < 3) or (month == 1 and day >= 7) or (month == 3 and day <= 23):
            cat_sum[2] += float(contents[item + 2].replace('$',''))
          #Spring Break
          elif (month == 3 and (day >= 24 or day <= 31)):
            cat_sum[3] += float(contents[item + 2].replace('$',''))
          #Spring
          elif (month > 4 and month < 6) or (month == 4 and day >= 0) or (month == 6 and day <= 14):
            cat_sum[4] += float(contents[item + 2].replace('$',''))
          #Summer Break
          else:
            pass

    # Month
    elif start == 4:
      cat_sum = [0] * 14
      summer_months = months[0:6] + ["Jun*"] + months[6:8] + ["Sep*"] + months[8:]
      for item in range(0, length - 3, 4): # Iterate over each "Date" cell
        if contents[item + 3] != "Assets": # Check type
          month = contents[item].split('-')[1]
          if month == "Jun" and int(contents[item].split('-')[0]) > 15:
            month = "Jun*"
          if month == "Sep" and int(contents[item].split('-')[0]) < 28:
            month = "Sep*"
          cat_sum[summer_months.index(month)] += float(contents[item + 2].replace('$',''))

    # Totals
    else:
      cat_sum = [0] * 3
      cat_sum[0] = sum(sums[12:18] + sums[22:26])
      cat_sum[1] = sum(sums[18:22])
      cat_sum[2] = sum([cat_sum[0], cat_sum[1]]) 

    sums += cat_sum # Append to final list for every iteration

  # Change to currency format and return
  sums = ["${:,.2f}".format(float(total)) for total in sums]
  return sums


# Verifies input
def validInput(user_input, pick, lst=[]):
  if pick == "File":
    while True:
      try:
        user_input = int(user_input)
        if user_input >= 0 and user_input < len(lst) + 1:
          return user_input - 1
        else:
          raise ValueError
      except ValueError:
        user_input = input("\nInvalid input. Try again\n>>> ")
  
  elif user_input in ["", "Exit", "exit"]:
    sys.exit("\nExited")
  
  elif pick == "date":
    while True:
      try:
        int(user_input.split('-')[0])

        if len(user_input.split('-')) == 2 and int(user_input.split('-')[0]) in days\
        and user_input.split('-')[1] in months:
          return user_input
        else:
          raise ValueError
      except ValueError:
        print("\nInvalid input")
        user_input = input("Date [dd-mmm]: ").title()

  elif pick == "Date":
    while True:
      if user_input in lst:
        return user_input
      else:
        print("\nInvalid input")
        user_input = input("Date [dd-mmm]: ").title()

  elif pick == "Description":
    while True:
      if user_input in lst:
        return user_input
      else:
        print("\nInvalid input")
        user_input = input("Description: ").title()

  elif pick == "description":
    return user_input

  elif pick == "Value":
    while True:
      try:
        float(user_input)
        return user_input
      except ValueError:
        print("\nInvalid input")
        user_input = input("Value [$]: ")

  elif pick == "Type":
    while True:
      # Valid type inputs
      big_types = [types.lower() for types in ea_types]
      bgl_types = [types[0] for types in ea_types]
      sml_types = [types.lower() for types in bgl_types]
      if user_input in ea_types + big_types + bgl_types + sml_types:
        return user_input
      else:
        print("\nInvalid input")
        user_input = input("Type {0}: ".format(ea_types))


# Convert list back to csv format
def listToCSV(lst):
  new_file, counter = "", 1
  for cell in lst:
    if counter < 4:
      new_file += str(cell) + ","
    else:
      new_file += str(cell) + "\n"
      counter = 0
    counter += 1
  return new_file


# Convert file to list
def fileToList(file):
  # Read file
  file = pd.read_csv(file_name, sep=",", header=-1)
  file.columns = ['Date', 'Description', 'Value', 'Category']
  file['Value'] = pd.DataFrame([str(value).replace(',','') for value in list(file['Value'])])

  # Combine dataframe columns to list
  contents = []
  length = getLength(file)
  for row in range(length + 33):
    for col in range(4):
      contents.append(file[file.columns[col]].tolist()[row])
  return contents


# Retrieves the highlights for stats
def getLight(stat, line, length):
  lights = ["\033[48;5;160m", "\033[48;5;171m", "\033[48;5;254m", 
  "\033[48;5;214m", "\033[48;5;76m", "\033[48;5;79m", "\033[48;5;239m"]

  if len(stat.split('-')) == 2: # Summer
    return "\033[48;5;251m" + "\033[38;5;0m" + stat + "\033[1;0m"
  elif stat in ea_types:
    return "".join(lights[ea_types.index(stat)]) + "\033[38;5;232m" + stat.ljust(15) + "\033[1;0m" + "".ljust(10)
  elif (line >= length + 84 and line <= length + 96) or line == length + 124:
    return "".join("\033[48;5;251m") + "\033[38;5;0m" + stat.ljust(15) + "\033[1;0m" + "".ljust(10)
  else:
    return stat.ljust(25)


# Retrieves the color for items
def getColor(type_of):
  color = ""
  for cat in ea_types:
    if type_of[0].upper() == cat[0]:
      return colors[ea_types.index(cat)] + chr(9608) + "\033[0m"
  return

# Length of all the expenses and assets
def getLength(contents):
  count = 0
  if type(contents) == list:
    for index in range(len(contents)):
      if str(contents[index]) in ['nan', '']:
        return count
      else:
        count += 1
  else:
    for index, row in contents[['Description']].iterrows():
      if pd.isna(row['Description']):
        return count
      else:
        count += 1

###############################################################################
file_name = select_file("*EA.csv")

action = ""
while not action:
  action = input("\nView, Add, Update, Delete, or Return? ")
  action = menu(action)