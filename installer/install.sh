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
	cp ./desktop/rotograph.desktop $HOME/.local/share/applications/
	$HOME/.local/bin/rotograph
fi
