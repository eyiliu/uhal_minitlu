#!/bin/bash

#HERE=$(readlink -f $(dirname $BASH_SOURCE))
HERE=$(python -c "import os.path; print os.path.dirname(os.path.abspath('$BASH_SOURCE'))")

CACTUSCORE_DIR=$HERE/../..
CACTUSCORE_UHAL_DIR=$HERE/..

export PATH=$CACTUSCORE_UHAL_DIR/tests/bin:$PATH
export PATH=$CACTUSCORE_UHAL_DIR/tests/src/python:$PATH
export PATH=$CACTUSCORE_UHAL_DIR/tests/scripts:$PATH
export PATH=$CACTUSCORE_UHAL_DIR/tools/scripts:$PATH
export PATH=$CACTUSCORE_DIR/extern/erlang/RPMBUILD/SOURCES/bin:$PATH
export PATH=$CACTUSCORE_DIR/controlhub/scripts:$PATH

export LD_LIBRARY_PATH=$CACTUSCORE_DIR/extern/boost/RPMBUILD/SOURCES/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CACTUSCORE_DIR/extern/pugixml/RPMBUILD/SOURCES/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/log/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/grammars/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/uhal/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/tests/lib:$LD_LIBRARY_PATH

UNAME=$(uname -s)
if [ "$UNAME" == "Darwin" ]; then 
export DYLD_LIBRARY_PATH=$CACTUSCORE_DIR/extern/boost/RPMBUILD/SOURCES/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$CACTUSCORE_DIR/extern/pugixml/RPMBUILD/SOURCES/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/log/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/grammars/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/uhal/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$CACTUSCORE_UHAL_DIR/tests/lib:$LD_LIBRARY_PATH
fi

export PYTHONPATH=$CACTUSCORE_UHAL_DIR/pycohal/pkg:$PYTHONPATH
#export PYTHONPATH=$CACTUSCORE_UHAL_DIR/gui:$PYTHONPATH

