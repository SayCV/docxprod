@chcp 65001
@echo off&SetLocal EnableDelayedExpansion
echo,
echo,=====
echo,SPDX-License-Identifier: (GPL-2.0+ OR MIT):
echo,
echo,!!! THIS IS NOT GUARANTEED TO WORK !!!
echo,
echo,Copyright (c) 2023, SayCV
echo,=====
echo,

cd /d "%~dp0"
set "TOPDIR=%cd:\=/%"
title "%~n0"

call conda info --envs 2>&1 | tee ../.%~n0.info
for /f "tokens=1-3 delims= " %%i in (../.%~n0.info) do (
    if "x%condaenv%" == "x" if not "x%%i" == "xbase" set condaenv=%%i
)
if exist ../.%~n0.info del ..\.%~n0.info

if not exist .../.condaenv.cmd echo set condaenv=%condaenv%>../.condaenv.cmd
call ../.condaenv.cmd

if not "x%condaenv%" == "x" call activate %condaenv%
if not "%errorlevel%" == "0" echo ::Please preset condaenv in .condaenvrc then run again && goto :eof_with_pause


set "DESTDIR=%TOPDIR%/../docxprod/data"
if not exist "%DESTDIR%" mkdir "%DESTDIR%"

set "SCRAPED_URLROOT=https://raw.githubusercontent.com/microsoft/vscode/main/extensions/markdown-language-features/media"
set "Referer=Referer: https://github.com"
set "UserAgent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"

set "FILENAME=markdown.css"
set "URL=%SCRAPED_URLROOT%/%FILENAME%"
set "dstfile=%DESTDIR%/%FILENAME%"
set "srcfile=%URL%"
echo Updating %FILENAME% ...
if "xy" == "xy" call curl -o "%dstfile%" "%srcfile%" -L -H "%Referer%" -H "%UserAgent%" -H "DNT: 1" --compressed
echo Updating complete.
if "xy" == "xy" if not !errorlevel! == 0 if exist "%dstfile%" del "%dstfile:/=\%" && pause && EXIT /B 1

if "%errorlevel%" == "0" goto :eof_with_exit
:eof_with_pause
pause
:eof_with_exit
goto :eof
