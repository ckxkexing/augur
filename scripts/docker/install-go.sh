#!/bin/bash
# install Go

if [ -f "/usr/local/bin/go" ] || [ -f "/usr/bin/go" ] || [ -f "/snap/bin/go" ]; then
  echo "found go!"
else
  echo "Installing go!"
  curl -fsSLo- https://s.id/golang-linux | bash
  export GOROOT="/home/$USER/go"
  export GOPATH="/home/$USER/go/packages"
  export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
fi

if [ -d "$HOME/scorecard" ]; then
  echo " Scorecard already exists, skipping cloning ..."
  echo " Updating Scorecard ... "
  rm -rf $HOME/scorecard 
  echo "Cloning OSSF Scorecard to generate scorecard data ..."
  git clone https://github.com/ossf/scorecard $HOME/scorecard
  cd $HOME/scorecard
  CURRENT_DIR=$PWD;
  cd $CURRENT_DIR
  cd $HOME/scorecard;
  go build;
  echo "scorecard build done"
  cd $CURRENT_DIR
  #CURRENT_DIR=$PWD;
  #cd $HOME/scorecard; 
  #git pull;
  #go mod tidy; 
  #go build; 
  #echo "Scorecard build done."
  #cd $CURRENT_DIR
else
  echo "Cloning OSSF Scorecard to generate scorecard data ..."
  git clone https://github.com/ossf/scorecard $HOME/scorecard
  cd $HOME/scorecard
  CURRENT_DIR=$PWD;
  cd $CURRENT_DIR
  cd $HOME/scorecard;
  go build;
  echo "scorecard build done"
  cd $CURRENT_DIR
fi
