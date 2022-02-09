#!/usr/bin/bash

if [ -d "$HOME/.local/share/rotograph" ] ; then
	  echo "Rotograph is already installed"
		echo "Would you like to remove it? (y/n)"
		read answer
		if [ "$answer" == "y" ] ; then
			rm -rf $HOME/.local/share/rotograph $HOME/.local/bin/rotograph $HOME/.local/share/applications/rotograph.desktop
			echo "Rotograph removed"
		else
			echo "Aborting"
		fi
else
	echo "Installing Rotograph"
	mkdir -p $HOME/.local/share/rotograph
	cp -r ./rotograph $HOME/.local/share/
	echo "Rotograph installed"
	ln -s $HOME/.local/share/rotograph/rotograph $HOME/.local/bin/rotograph
	echo "[Desktop Entry]" > $HOME/.local/share/applications/rotograph.desktop
	echo "Encoding=UTF-8" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Version=1.0rc1" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Type=Application" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Terminal=false" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Exec=$HOME/.local/bin/rotograph" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Name=Rotograph" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Icon=$HOME/.local/share/rotograph/assets/Icon.png" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Categories=Graphics;" >> $HOME/.local/share/applications/rotograph.desktop
	echo "Comment=A simple rotograph camera written in Python" >> $HOME/.local/share/applications/rotograph.desktop
	$HOME/.local/bin/rotograph
fi
