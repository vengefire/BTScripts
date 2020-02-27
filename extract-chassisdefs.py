import os
import shutil
import re


if __name__ == '__main__':
    missing_csv_file = r'C:\Users\vf\Documents\missing.csv'
    search_directory = r'C:\Users\vf\gitrepos\RogueTech'
    target_directory = r'c:\tmp\missing_chassis'
    missing_chassisDefs = []
    found_chassisDefs = []
    with open(missing_csv_file) as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split(',')
            chassisName = parts[1].replace(' ', '_')
            chassisDefName = f'chassisdef_{chassisName}.json'
            missing_chassisDefs.append(chassisDefName.lower())

    for root, dirs, files in os.walk(search_directory):
        for file in files:
            if file.lower() in missing_chassisDefs:
                found_chassisDefs.append((file, os.path.join(root, file)))

    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
        # os.rmdir(target_directory)

    os.mkdir(target_directory)

    [print(f'{found[0]}') for found in found_chassisDefs]

    for found in found_chassisDefs:
        source = found[1]
        target = os.path.join(target_directory, found[0])
        print(f'Found [{found[0]}] at [{source}], copying to [{target}]')
        shutil.copyfile(source, target)
