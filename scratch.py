#       Batch 360, 01:03
IM = ImageProcessingManager()
list_of_random_images = select_random_images(data_directory, 100)
for random_image in list_of_random_images:
    override_image = 0
    if override_image:
        random_image = override_image
    ballot_image = Image.open(random_image)
    ballot_bitmap = np.asarray(ballot_image)
    cursor = ScanningCursor()
    print("\n\neog " + random_image + "&")
    print(f"\"{random_image}\"")
    locations_of_top_bars, locations_of_side_bars, locations_of_bottom_bars, \
    left_bar_data, right_bar_data = cursor.get_border_bars(ballot_bitmap)

    print(locations_of_top_bars[0][1] - locations_of_top_bars[0][0], locations_of_top_bars[0:2],
          locations_of_top_bars[-1], locations_of_top_bars[-1][1] - locations_of_top_bars[-1][0])
    print(locations_of_side_bars[0][1] - locations_of_side_bars[0][0], locations_of_side_bars[0:2],
          locations_of_side_bars[-1], locations_of_side_bars[-1][1] - locations_of_side_bars[-1][0])
    print(locations_of_bottom_bars[0][1] - locations_of_bottom_bars[0][0], locations_of_bottom_bars[0:2],
          locations_of_bottom_bars[-1], locations_of_bottom_bars[-1][1] - locations_of_bottom_bars[-1][0])
    print(f"Left bar data: {left_bar_data}")
    print(f"Right bar data: {right_bar_data}")



    data_directory, data_has_been_downloaded, browser_type, download_directory = main.load_configuration_information()
    barcodes = scan_all_barcodes(data_directory)
    save_file = open("barcodes.json",'w')
    save_file.write(json.dumps(barcodes))
    save_file.close()
    print(barcodes)

    override_image = 0
    if override_image:
        random_image = override_image
    ballot_image = Image.open(random_image)
    ballot_bitmap = np.asarray(ballot_image)
    ballot_image.close()
    print("\n\neog " + random_image + "&")
    print(f"\"{random_image}\"")
    try:
        serial_number = get_serial_number(ballot_bitmap)
        print(serial_number)
    except:
        print("Error")


