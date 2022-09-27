#!/bin/bash

set -e

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=$("${HERE}/bin-Linux/verifyta" -v | head -n 1 | awk '{ print $3 }')
NAME="Uppaal-${VERSION}"
SCRIPT="$0"

testcommand() {
    command -v "$1" >/dev/null 2>&1 || {
	echo >&2 "${SCRIPT} requires $1 but it is not installed. Aborting."
	exit 1
    }
}

echo -n "Checking that xdg-utils are installed... "
for c in xdg-mime xdg-icon-resource xdg-desktop-icon xdg-desktop-menu ; do
    testcommand "${c}"
done
echo "OK"

echo -n "Installing Uppaal icons... "
for s in 16 24 32 48 64 96 128 ; do
    icon="${HERE}/res/icon-"$s"x"$s".png"
    if [ -e "${icon}" ] ; then
	xdg-icon-resource install --context apps --size $s "${icon}" uppaal-icon
	xdg-icon-resource install --context mimetypes --size $s "${icon}" application-uppaal-xml
    fi
done
echo "OK"

echo -n "Installing desktop and menu icons... "
LAUNCHER="${HOME}/.local/share/applications/${NAME}.desktop"
cat > "${LAUNCHER}" << EOF
[Desktop Entry]
Encoding=UTF-8
Version=1.0
Type=Application
GenericName=Model Checker
Name=${NAME}
Comment=Verify timed automata models
Exec="${HERE}/uppaal" %u
Icon=uppaal-icon
Categories=Application;Science;Math;Education;Development;IDE
Terminal=false
StartupNotify=true
MimeType=application/uppaal-xml;application/uppaal-xta;application/vnd.uppaal-xml;application/vnd.uppaal-xta;application/x-uppaal-xml;application/x-uppaal-xta
EOF
xdg-desktop-icon install --novendor "${LAUNCHER}"
xdg-desktop-menu install --novendor "${LAUNCHER}"
echo "OK"

echo -n "Installing mime-type associations for Uppaal files... "

xdg-mime install "${HERE}/res/uppaal-xml-mimetype.xml"
xdg-mime install "${HERE}/res/uppaal-xta-mimetype.xml"
xdg-mime install "${HERE}/res/uppaal-ta-mimetype.xml"
xdg-mime install "${HERE}/res/uppaal-ugi-mimetype.xml"

xdg-mime default "${LAUNCHER}" "application/uppaal-xml"
xdg-mime default "${LAUNCHER}" "application/uppaal-xta"
xdg-mime default "${LAUNCHER}" "application/uppaal-ta"

update-mime-database ~/.local/share/mime
update-desktop-database ~/.local/share/applications

echo "OK"

