import sys
import site
import os


def print_python_path():
    print("Python Path:")
    for path in sys.path:
        print(f"  - {path}")


def find_package_link(package_name):
    for path in site.getsitepackages():
        egg_link = os.path.join(path, f"{package_name}.egg-link")
        if os.path.exists(egg_link):
            with open(egg_link, "r") as f:
                return f.read().strip()
    return None


def main():
    print("Python Version:", sys.version)
    print("\nPython Executable:", sys.executable)
    print("\nSite Packages:")
    for path in site.getsitepackages():
        print(f"  - {path}")

    package_name = input("\nEnter your package name: ")
    package_location = find_package_link(package_name)
    if package_location:
        print(f"\nPackage '{package_name}' is installed in editable mode at:")
        print(f"  {package_location}")
    else:
        print(f"\nPackage '{package_name}' not found in editable mode.")

    print_python_path()


if __name__ == "__main__":
    main()
