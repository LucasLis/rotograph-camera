#!/usr/bin/bash

if [ -d "$HOME/.local/share/rotograph" ] ; then
	  echo "Rotograph is already installed"
		echo "Would you like to remove it? (y/n)"
		read answer
		if [ "$answer" == "y" ] ; then
			rm -rf $HOME/.local/share/rotograph $HOME/.local/bin/rotograph $HOME/.local/share/applications/Rotograph.desktop $HOME/Desktop/Rotograph.desktop
			echo "Rotograph removed"
		else
			echo "Aborting"
		fi
else
	echo "Installing Rotograph"
	mkdir -p $HOME/.local/share/rotograph
	cp -r ./rotograph $HOME/.local/share/
	chmod u+x $HOME/.local/share/rotograph/rotograph
	echo "Rotograph installed"
	mkdir -p $HOME/.local/bin
	ln -s $HOME/.local/share/rotograph/rotograph $HOME/.local/bin/rotograph
	echo "[Desktop Entry]" > $HOME/.local/share/applications/Rotograph.desktop
	echo "Encoding=UTF-8" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Version=1.0" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Type=Application" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Terminal=false" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Exec=$HOME/.local/bin/rotograph" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Name=Rotograph Camera" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Icon=$HOME/.local/share/rotograph/assets/Icon.png" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Categories=Graphics;" >> $HOME/.local/share/applications/Rotograph.desktop
	echo "Comment=A simple rotograph camera written in Python" >> $HOME/.local/share/applications/Rotograph.desktop
	chmod u+x $HOME/.local/share/applications/Rotograph.desktop
	if [ -d "$HOME/Desktop" ] ; then
		cp $HOME/.local/share/applications/Rotograph.desktop $HOME/Desktop/
		chmod u+x $HOME/Desktop/Rotograph.desktop
		echo "Rotograph application added to your desktop"
	else
		echo "Desktop folder not found"
	fi
	$HOME/.local/bin/rotograph
fi
