#!/usr/bin/bash

echo "Note: If you are on debian (such as on a Raspberry Pi) you will need to install the following packages:"
echo "sudo apt-get install python3-opengl"

read -p "Press enter to continue"

function remove {
	rm -rf $HOME/.local/share/rotograph $HOME/.local/bin/rotograph $HOME/.local/share/applications/Rotograph.desktop $HOME/Desktop/Rotograph.desktop
}

if [ -d "$HOME/.local/share/rotograph" ] ; then
	echo "Rotograph is already installed"
	read -p "Would you like to remove it? (y/n) " answer
	if [ "$answer" == "y" ] ; then
		remove
		echo "Rotograph removed"
		if [ -d "$HOME/.config/rotograph" ] ; then
			read -p "Delete configuration files? (y/n) " answer
			if [ "$answer" == "y" ] ; then
				rm -rf $HOME/.config/rotograph
				echo "Configuration files removed"
			fi
		fi
	else
		echo "Aborting"
	fi
else
	echo "Installing Rotograph"
	# Copy data
	mkdir -p $HOME/.local/share/rotograph
	cp -r ./rotograph $HOME/.local/share/
	if [ $? -eq 0 ] ; then
		echo "Copied rotograph to ~/.local/share/rotograph"
	else
		echo "Failed to copy rotograph to ~/.local/share/rotograph"
		remove
		exit 1
	fi
	# Make executable
	chmod u+x $HOME/.local/share/rotograph/rotograph
	if [ $? -eq 0 ] ; then
		echo "Made rotograph executable"
	else
		echo "Failed to make rotograph executable"
		remove
		exit 1
	fi
	# Link to bin folder
	mkdir -p $HOME/.local/bin
	ln -s $HOME/.local/share/rotograph/rotograph $HOME/.local/bin/rotograph
	if [ $? -eq 0 ] ; then
		echo "Linked rotograph to ~/.local/bin/rotograph"
	else
		echo "Failed to link rotograph to ~/.local/bin/rotograph"
		remove
		exit 1
	fi
	# Create desktop file
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
	echo "Created desktop file"
	if [ -d "$HOME/Desktop" ] ; then
		cp $HOME/.local/share/applications/Rotograph.desktop $HOME/Desktop/
		chmod u+x $HOME/Desktop/Rotograph.desktop
		echo "Rotograph application added to your desktop"
	else
		echo "Desktop folder not found"
	fi
	echo "Rotograph installed"
	read -p "Press enter to continue"
	# Launch rotograph for first-time setup
	echo "Launching Rotograph for first-time setup"
	$HOME/.local/bin/rotograph
fi
