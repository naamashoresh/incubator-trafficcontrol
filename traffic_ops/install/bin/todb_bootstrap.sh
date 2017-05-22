#!/usr/bin/env bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# To bypass the password prompts for automation, please set TODB_USERNAME_PASSWORD=<yourpassword> before you invoke

# Example:
#
#    $ TODB_USERNAME_PASSWORD=<yourpassword> ./todb_bootstrap.sh
#
TODB_USERNAME=traffic_ops
TODB_NAME=traffic_ops

if [[ -z $TODB_USERNAME ]]; then
    echo "Using environment database user: $TODB_USERNAME"
fi

if [[ -z $TODB_USERNAME_PASSWORD ]]; then
   while true; do
    read -s -p "Please ENTER the new password for database user '$TODB_USERNAME': " password
    echo
    read -s -p "Please CONFIRM enter the new password for database user '$TODB_USERNAME' again: " password_confirm
    echo
    [ "$password" = "$password_confirm" ] && break
    echo "Passwords do not match, please try again"
   done
   TODB_USERNAME_PASSWORD=$password
else
    echo "Using environment database password"
fi
echo "Setting up database role: $TODB_USERNAME"
psql -U postgres -h localhost -c "CREATE USER $TODB_USERNAME WITH ENCRYPTED PASSWORD '$TODB_USERNAME_PASSWORD';"
createdb $TODB_NAME --owner $TODB_USERNAME -U postgres -h localhost

echo "Successfully set up database '$TODB_NAME' with role '$TODB_USERNAME'"
