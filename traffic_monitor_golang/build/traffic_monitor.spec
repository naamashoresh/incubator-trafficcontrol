#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# RPM spec file for the Go version of Traffic Monitor (tm).
#
%define debug_package %{nil}
Name:		traffic_monitor
Version:        %{traffic_control_version}
Release:        %{build_number}
Summary:	Monitor the caches
Packager:	david_neuman2 at Cable dot Comcast dot com
Vendor:		Apache Software Foundation
Group:		Applications/Communications
License:	Apache License, Version 2.0
URL:		https://github.com/apache/incubator-trafficcontrol
Source:		%{_sourcedir}/traffic_monitor-%{traffic_control_version}.tgz

%description
Installs traffic_monitor

%prep

%setup

%build
export GOPATH=$(pwd)
# Create build area with proper gopath structure
mkdir -p src pkg bin || { echo "Could not create directories in $(pwd): $!"; exit 1; }

go_get_version() {
  local src=$1
  local version=$2
  (
   cd $src && \
   git checkout $version && \
   go get -v \
  )
}

# get traffic_ops client
godir=src/github.com/apache/incubator-trafficcontrol/traffic_ops/client
( mkdir -p "$godir" && \
  cd "$godir" && \
  cp -r "$TC_DIR"/traffic_ops/client/* . && \
  go get -v \
) || { echo "Could not build go program at $(pwd): $!"; exit 1; }

#build traffic_monitor binary
godir=src/github.com/apache/incubator-trafficcontrol/traffic_monitor_golang
oldpwd=$(pwd)
( mkdir -p "$godir" && \
  cd "$godir" && \
  cp -r "$TC_DIR"/traffic_monitor_golang/* . && \
  cd traffic_monitor && \
  go get -d -v && \
  go build -ldflags "-X main.GitRevision=`git rev-parse HEAD` -X main.BuildTimestamp=`date +'%Y-%M-%dT%H:%M:%s'` -X main.Version=%{traffic_control_version}" \
) || { echo "Could not build go program at $(pwd): $!"; exit 1; }

%install
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor/bin
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor/conf
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor/backup
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor/static
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor/var/run
mkdir -p "${RPM_BUILD_ROOT}"/opt/traffic_monitor/var/log
mkdir -p "${RPM_BUILD_ROOT}"/etc/init.d
mkdir -p "${RPM_BUILD_ROOT}"/etc/logrotate.d

src=src/github.com/apache/incubator-trafficcontrol/traffic_monitor_golang
cp -p "$src"/traffic_monitor/traffic_monitor     "${RPM_BUILD_ROOT}"/opt/traffic_monitor/bin/traffic_monitor
cp  "$src"/traffic_monitor/static/index.html     "${RPM_BUILD_ROOT}"/opt/traffic_monitor/static/index.html
cp  "$src"/traffic_monitor/static/sorttable.js     "${RPM_BUILD_ROOT}"/opt/traffic_monitor/static/sorttable.js
cp "$src"/conf/traffic_ops.cfg        "${RPM_BUILD_ROOT}"/opt/traffic_monitor/conf/traffic_ops.cfg
cp "$src"/conf/traffic_monitor.cfg        "${RPM_BUILD_ROOT}"/opt/traffic_monitor/conf/traffic_monitor.cfg
cp "$src"/build/traffic_monitor.init       "${RPM_BUILD_ROOT}"/etc/init.d/traffic_monitor
cp "$src"/build/traffic_monitor.logrotate  "${RPM_BUILD_ROOT}"/etc/logrotate.d/traffic_monitor

%pre
/usr/bin/getent group traffic_monitor >/dev/null

if [ $? -ne 0 ]; then

	/usr/sbin/groupadd -g 423 traffic_monitor
fi

/usr/bin/getent passwd traffic_monitor >/dev/null

if [ $? -ne 0 ]; then

	/usr/sbin/useradd -g traffic_monitor -u 423 -d /opt/traffic_monitor -M traffic_monitor

fi

/usr/bin/passwd -l traffic_monitor >/dev/null
/usr/bin/chage -E -1 -I -1 -m 0 -M 99999 -W 7 traffic_monitor

if [ -e /etc/init.d/traffic_monitor ]; then
	/sbin/service traffic_monitor stop
fi

#don't install over the top of java TM.  This is a workaround since yum doesn't respect the Conflicts tag.
if [[ $(rpm -q traffic_monitor --qf "%{VERSION}-%{RELEASE}") < 1.9.0 ]]
then
    echo -e "\n****************\n"
    echo "A java version of traffic_monitor is installed.  Please backup/remove that version before installing the golang version of traffic_monitor."
    echo -e "\n****************\n"
    exit 1
fi

%post

/sbin/chkconfig --add traffic_monitor
/sbin/chkconfig traffic_monitor on

%files
%defattr(644, traffic_monitor, traffic_monitor, 755)
%config(noreplace) /opt/traffic_monitor/conf/traffic_monitor.cfg
%config(noreplace) /opt/traffic_monitor/conf/traffic_ops.cfg
%config(noreplace) /etc/logrotate.d/traffic_monitor

%dir /opt/traffic_monitor
%dir /opt/traffic_monitor/bin
%dir /opt/traffic_monitor/conf
%dir /opt/traffic_monitor/backup
%dir /opt/traffic_monitor/static
%dir /opt/traffic_monitor/var
%dir /opt/traffic_monitor/var/log
%dir /opt/traffic_monitor/var/run

%attr(600, traffic_monitor, traffic_monitor) /opt/traffic_monitor/conf/*
%attr(600, traffic_monitor, traffic_monitor) /opt/traffic_monitor/static/*
%attr(755, traffic_monitor, traffic_monitor) /opt/traffic_monitor/bin/*
%attr(755, traffic_monitor, traffic_monitor) /etc/init.d/traffic_monitor

%preun
# args for hooks: http://www.ibm.com/developerworks/library/l-rpm2/
# if $1 = 0, this is an uninstallation, if $1 = 1, this is an upgrade (don't do anything)
if [ "$1" = "0" ]; then
	/sbin/chkconfig traffic_monitor off
	/etc/init.d/traffic_monitor stop
	/sbin/chkconfig --del traffic_monitor
fi
