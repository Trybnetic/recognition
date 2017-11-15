#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def to_long_format(file_path, output_path):
    with open(file_path, "r") as raw_file:
        content = raw_file.read()
        lines = content.split("\n")

        firstline, secondline, *lines, lastline = lines

        for char in ["#","{","}","'"]:
            firstline = firstline.replace(char," ")

        var_list = list()
        for elem in firstline.split(","):
            key, val = elem.split(":")
            var_list.append(val.strip())

        semester, ses_file, student, age, time_stamp, id_, sex = var_list

        group = ses_file[6]

    with open(output_path, "a") as out_file:
        trial = 1
        for line in lines:
            out_file.write(line + ";%s;%s;%s;%s;%s;%s;%s\n" % (semester,
                                                            student,
                                                            age,
                                                            id_,
                                                            sex,
                                                            group,
                                                            trial))
            trial += 1

        if lastline:
            out_file.write(lastline + ";%s;%s;%s;%s;%s;%s;%s\n" % (semester,
                                                                student,
                                                                age,
                                                                id_,
                                                                sex,
                                                                group,
                                                                trial))



FILES = [os.path.join("recognition/", file_)
         for file_ in os.listdir("recognition/")
         if os.path.isfile(os.path.join("recognition/", file_))]

DATA_FILE = "recognition-data.txt"
with open(DATA_FILE, "w") as out_file:
    out_file.write("city_left;city_right;response;rt;semester;student;age;id;sex;group;trial\n")
for file_ in FILES:
    to_long_format(file_, DATA_FILE)
