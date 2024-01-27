"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 20/12/2023
@Description  :
"""
from app.services.db.operations import Matcher, Registrar


def test_matcher():
    ins_1 = Matcher()





def test_registrar():
    ins_2 = Registrar()

    ins_2.insert_fake_face(10000)



if __name__=="__main__":
    test_matcher()
    test_registrar()
