#!/bin/bash
###############################################################################
#
# Copyright (C) 2025 Tom Kralidis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

# Configuration
BASEDIR="/data/web/msc-wis2node-nightly"
MSC_WIS2NODE="https://github.com/ECCC-MSC/msc-wis2node.git"
DAYSTOKEEP=7

# Derived variables
DATETIME=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d.%H%M)
NIGHTLYDIR="msc-wis2node-$TIMESTAMP"

echo "### Deleting nightly builds older than $DAYSTOKEEP days ###"

# Ensure base directory exists
if [[ ! -d $BASEDIR ]]; then
    echo "Error: Base directory $BASEDIR does not exist."
    exit 1
fi

cd "$BASEDIR" || exit

# Find and delete old directories
find . -type d -name "msc-wis2node-20*" -mtime +$DAYSTOKEEP -exec rm -rf {} \; \
    && echo "Deleted directories older than $DAYSTOKEEP days."

# Remove the `latest` symlink
if [[ -L latest ]]; then
    rm -f latest && echo "Removed old 'latest' symlink."
fi

echo "### Generating nightly build for $TIMESTAMP ###"

# Create and navigate to the new nightly build directory
mkdir "$NIGHTLYDIR" && cd "$NIGHTLYDIR" || exit

# Clone the repository
echo "Cloning Git repository from $MSC_WIS2NODE..."
if git clone "$MSC_WIS2NODE" --depth=1; then
    echo "Git repository cloned successfully."
else
    echo "Error: Failed to clone repository."
    exit 1
fi

# cd into cloned repository directory
cd "$(basename "$MSC_WIS2NODE" .git)" || exit

cp $BASEDIR/msc-wis2node.env .
chmod 400 msc-wis2node.env

# Docker operations
echo "Stopping, building, and starting Docker setup..."
make force-build
make down
make up

cat > $NIGHTLYDIR/msc-wis2node-nightly.conf <<EOF
<Location /msc-wis2node>
  ProxyPass http://localhost:4326/
  ProxyPassReverse http://localhost:4326/
  Header set Access-Control-Allow-Origin "*"
  Header set Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization"
  Require all granted
</Location>
EOF

# Navigate back to base directory
cd "$BASEDIR" || exit

# Create the 'latest' symlink
ln -s "$NIGHTLYDIR" latest && echo "Symlink 'latest' created for $NIGHTLYDIR."

echo "### Nightly build process completed successfully ###"
