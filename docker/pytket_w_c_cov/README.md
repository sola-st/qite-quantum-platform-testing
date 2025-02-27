## Build the Docker

```bash
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t pytket_w_c .
```

## Run the Docker and Collect Coverage of CPP Files

```bash
docker run -it --rm \
    -v $(pwd)/container_accessible_folder:/home/regularuser/host \
    -v $(pwd)/base_qc_w_opt.py:/home/regularuser/tket/base_qc_w_opt.py \
    pytket_w_c /bin/bash


# inside the container

source /home/regularuser/.venv/bin/activate

# run python scripts exercising pytket
python /home/regularuser/tket/base_qc_w_opt.py

# get path to the covereage data infos
export GCDA_PATH=$(find /home/regularuser/.conan2/p/b/tket* -name "*.gcda" | grep -o '.*/Debug' | head -n 1) && echo $GCDA_PATH

# create the report
gcovr --print-summary --xml-pretty --xml -r ${GCDA_PATH}/../../src/ --exclude-lines-by-pattern='.*\bTKET_ASSERT\(.*\);' --object-directory=${GCDA_PATH}/CMakeFiles/tket.dir/src -o /home/regularuser/host/cpp_coverage.xml --decisions
```


# Generic Notes

```bash
# prepare the environment
conan profile detect && \
DEFAULT_PROFILE_PATH=$(conan profile path default) && \
PROFILE_PATH=./conan-profiles/ubuntu-24.04 && \
diff ${DEFAULT_PROFILE_PATH} ${PROFILE_PATH} || true && \
cp ${PROFILE_PATH} ${DEFAULT_PROFILE_PATH} && \
conan remote add tket-libs https://quantinuumsw.jfrog.io/artifactory/api/conan/tket1-libs --index 0


# conan install
conan install --requires tket/1.3.32@tket/stable -o "boost/*":header_only=True -o "tklog/*":shared=True -o "tket/*":shared=True -o "tket/*":profile_coverage=True -o "test-tket/*":with_coverage=True -o with_test=True --build=tket/1.3.32@tket/stable
# check output
# Full package reference: tket/1.3.32@tket/stable#05f3cc1769d861dae37b1cb3164f965a:d93eb7a27a80e130093ea1e9f30bb0e8bc56f4a8#f0ddb6c85bbbbbee1e0bd14341784930

conan cache path tket/1.3.32@tket/stable#05f3cc1769d861dae37b1cb3164f965a:d93eb7a27a80e130093ea1e9f30bb0e8bc56f4a8#f0ddb6c85bbbbbee1e0bd14341784930 --folder=build
# /home/regularuser/.conan2/p/b/tkete57ed68c585b2/b
```

## Attempt 1

```
conan create tket --version 1.3.32 --user=tket --channel=stable --build="tket*" -o "boost/*":header_only=True -o "tklog/*":shared=True -o "tket/*":shared=True -tf "" -s build_type=Debug -o "tket/*":profile_coverage=True

cd pytket && pip install -e . -v && pip install -r tests/requirements.txt
```

## Attempt 2

```shell
# export CFLAGS="--coverage"
# export CC="ccache gcc"

# conan cache clean --locks --sources --builds --download
source /home/regularuser/.venv/bin/activate


# conan create tket --version 1.3.32 --user=tket --channel=stable --build="tket*" -o "boost/*":header_only=True -o "tklog/*":shared=True -o "tket/*":shared=True -tf "" -s build_type=Debug -o "tket/*":profile_coverage=True
# # get the full path and get its build folder
# conan cache path tket/1.3.32@tket/stable#05f3cc1769d861dae37b1cb3164f965a:09694e74c8f72ea77079b8a2a88268efb2daccac#02b03e4085f417590f9ec8517b81a769 --folder=build
# # OUTPUT: /home/regularuser/.conan2/p/b/tkete2966097f0400/b


# export CFLAGS="--coverage" && export CC="ccache gcc" && export CMAKE_CXX_FLAGS="$CMAKE_CXX_FLAGS --coverage" && conan remove tket*
# replace "--build=missing" with "--build='tket*'"
# in pytket/setup.py

# sed -i 's/"--build=missing",/"--build=tket*"/' pytket/setup.py

# Replace "--build=missing" with the specified options in pytket/setup.py
sed -i 's/"--build=missing",/"--build=missing", "-o", '\''tket\/\*:profile_coverage=True'\'', "-s", "build_type=Debug",/' pytket/setup.py

# sed -i 's/"tket\/\*"/tket\/\*/' pytket/setup.py



# Print the new file content
cat pytket/setup.py

# DESIRED CONTENT
# jsonstr = subprocess.check_output(
#     [
#         "conan",
#         "create",
#         ".",
#         "--build=missing", "-o", 'tket/*:profile_coverage=True', "-s", "build_type=Debug",
#         "-o",
#         "boost/*:header_only=True",
#         "-o",
#         "tket/*:shared=True",
#         "-o",
#         "tklog/*:shared=True",
#         "--format",
#         "json",
#     ],
#     cwd=extsource,
# )


# build tket locally first
# conan create tket --version 1.3.32 --user=tket --channel=stable -s build_type=Debug --build=missing -o "boost/*":header_only=True -o "tket/*":profile_coverage=True -o "tket/*:shared=True" -o "tklog/*:shared=True" -tf ""
# ALTERNATIVE TO TRY:
# conan create tket --version 1.3.32 --user=tket --channel=stable -s build_type=Debug --build=missing -o "boost/*":header_only=True -o "tket/*:profile_coverage=True" -o "tket/*:shared=True" -o "tklog/*:shared=True" -tf ""

conan remove -c "pybind11/*" && \
conan create recipes/pybind11 -s build_type=Debug -o "tket/*":profile_coverage=True && \
conan create recipes/pybind11_json/all --version=0.2.14  -s build_type=Debug -o "tket/*":profile_coverage=True



# sed -i 's/"--build=missing",/"--build=tket*", "-o", '\''"tket/*":profile_coverage=True/' pytket/setup.py
# \n"tket/*":profile_coverage=True \n-s \nbuild_type=Debug' pytket/setup.py
# print the new file content
cat pytket/setup.py


# problem pytket is using a different version of tket, not the one built above
cd pytket && pip install -e . -v && pip install -r tests/requirements.txt
# run program
python /home/regularuser/tket/base_qc_w_opt.py

# check the gcda presence
export GCDA_PATH=$(find /home/regularuser/.conan2/p/b/tket* -name "*.gcda" | grep -o '.*/Debug' | head -n 1) && echo $GCDA_PATH

su
apt-get install -y gcovr
cd /home/regularuser/tket
gcovr --print-summary --xml-pretty --xml -r ${GCDA_PATH}/../../src/ --object-directory=${GCDA_PATH}/CMakeFiles/tket.dir/src -o cpp_coverage.xml

# delete all the gcda files in the folder
find /home/regularuser/.conan2/p/b/tket* -name "*.gcda" -delete



```



## Attempt 3

```shell
# remove
conan remove tket*
# install tket with the test and get coverage from it
conan build tket --user=tket --channel=stable -s build_type=Debug --build=missing -o "boost/*":header_only=True -o "tket/*":profile_coverage=True -o "test-tket/*":with_coverage=True -o with_test=True -of build/tket


mkdir test-coverage
gcovr --print-summary --xml-pretty --xml -r ./tket --exclude-lines-by-pattern='.*\bTKET_ASSERT\(.*\);' --object-directory=${PWD}/build/tket/build/Debug/CMakeFiles/tket.dir/src -o test-coverage/coverage.xml --decisions

```

# tket

```txt


======== Input profiles ========
Profile host:
[settings]
arch=x86_64
build_type=Debug
compiler=gcc
compiler.cppstd=gnu17
compiler.libcxx=libstdc++11
compiler.version=13
os=Linux
[options]
boost/*:header_only=True
tket/*:profile_coverage=True
tket/*:shared=True
tklog/*:shared=True

Profile build:
[settings]
arch=x86_64
build_type=Release
compiler=gcc
compiler.cppstd=gnu17
compiler.libcxx=libstdc++11
compiler.version=13
os=Linux
```

# pytket
```txt
  ======== Input profiles ========
  Profile host:
  [settings]
  arch=x86_64
  build_type=Debug
  compiler=gcc
  compiler.cppstd=gnu17
  compiler.libcxx=libstdc++11
  compiler.version=13
  os=Linux
  [options]
  "tket/*":profile_coverage=True
  boost/*:header_only=True
  tket/*:shared=True
  tklog/*:shared=True

  Profile build:
  [settings]
  arch=x86_64
  build_type=Release
  compiler=gcc
  compiler.cppstd=gnu17
  compiler.libcxx=libstdc++11
  compiler.version=13
  os=Linux
```
