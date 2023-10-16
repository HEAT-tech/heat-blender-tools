import os
import zipfile
from global_vars import VERSION

dir_to_zip = os.getcwd()

output_zip = f'build/HeatBlender-v{VERSION}.zip'
print(f'Writing to zip file: {output_zip}')

if not os.path.exists(os.path.dirname(output_zip)):
    print('creating build dir...')
    os.makedirs(os.path.dirname(output_zip))

# List of files and subdirectories to be excluded from the zip file
exclude_list = ['.git', '.env', '_git_assets', 'local_server.log', 'addon - heatblender_updater', 'build', 'Readme.MD', '__pycache__', '.gitignore']
print(f'excluding...{exclude_list}')

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zip:
    for root, dirs, files in os.walk(dir_to_zip):
        # Remove any excluded files or directories from the list
        dirs[:] = [d for d in dirs if d not in exclude_list]

        # If we're in the 'dependencies' directory, exclude subdirectories with the naming convention "heat-tools-*"
        if 'dependencies' in root:
            dirs[:] = [d for d in dirs if not d.startswith('heat-tools-')]

        files[:] = [f for f in files if f not in exclude_list]

        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, dir_to_zip)
            print(f'Compressing...{arcname}')
            zip.write(file_path, arcname=os.path.join('HeatBlender', arcname))

print('done')
