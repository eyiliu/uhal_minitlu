#!/bin/bash
if [[ $_ != $0 ]]; then 
  echo "$BASH_SOURCE is meant to be executed:"
  echo "  ./$BASH_SOURCE"
  return 0
fi


#------------------------------------------------------------------------------
# Step 1
#
# Ensure the tag directory is there
HERE=$PWD
TAG_HOME="/build/tags"
sudo mkdir -p ${TAG_HOME}
sudo chmod 777 ${TAG_HOME}

PKG_MAJOR=1
PKG_MINOR=0
PKG_PATCH=8

TAG_ID="amc13_v${PKG_MAJOR}_${PKG_MINOR}_${PKG_PATCH}"
TAG_TITLE="AMC13 Software (v${PKG_MAJOR}.${PKG_MINOR}.${PKG_PATCH})"

#
# Check the tag out in /build/tags

SVN_TAG="amc13/${TAG_ID}"
SVN_CO="svn co svn+ssh://cactus@svn.cern.ch/reps/cactus/tags/"
SVN_TARGET="${TAG_HOME}/${SVN_TAG}"
set -x

# Cleanup previous checouts
rm -rf ${SVN_TARGET}

mkdir -p ${SVN_TARGET}

# Checkout!
cmd="${SVN_CO}${SVN_TAG} ${SVN_TARGET}"
$cmd
set +x

#------------------------------------------------------------------------------
# Step 2
#
# Set up the doxy environment
# Similat to the nightly scripts
CACTUS_RELEASES="/afs/cern.ch/user/c/cactus/www/release/"


export DOXYGEN_HOME=${HOME}/doxygen/doxygen-1.8.6/
# export CACTUS_SANDBOX=/build/cactus/cactus/trunk
export CACTUS_SANDBOX=${SVN_TARGET}
export API_DIR=${CACTUS_RELEASES}/amc13/1.0/api # <--- points to the release folder
export DOXYGEN_OUTPUT=/tmp/tags/api_amc13/   # <--- added tags, not to mess with the nightlies
export DOXYGEN_WWW=${API_DIR}/html

cd ${HOME}/nightly/doxygen
echo "Cleaning up target directory"
rm -r ${DOXYGEN_OUTPUT}/html

# DOXYGEN_MAINPAGE="${CACTUS_SANDBOX}/cactusupgrades/boards/amc13/software/amc13/README.md"
# DOXYGEN_INPUTS="${CACTUS_SANDBOX}/cactusupgrades/boards/amc13/software/amc13 "
# DOXYGEN_PROJECT_NAME='AMC13 Software (nightly)'
DOXYGEN_MAINPAGE="${CACTUS_SANDBOX}/README.md"
DOXYGEN_INPUTS="${CACTUS_SANDBOX}"
DOXYGEN_PROJECT_NAME="AMC13 Software (v${PKG_MAJOR}.${PKG_MINOR}.${PKG_PATCH})"
DOXYGEN_EXCLUDE_PATTERNS=''

echo DOXYGEN_INPUTS=${DOXYGEN_INPUTS}
export DOXYGEN_MAINPAGE DOXYGEN_INPUTS DOXYGEN_PROJECT_NAME
mkdir -p ${DOXYGEN_OUTPUT}
${DOXYGEN_HOME}/bin/doxygen cactus-v3.doxy

echo "Removing old APIs"
rm -r ${DOXYGEN_WWW}

echo "Uploading..."
mkdir -p ${API_DIR}
cp -a ${DOXYGEN_OUTPUT}/html ${DOXYGEN_WWW}
echo "Done"
