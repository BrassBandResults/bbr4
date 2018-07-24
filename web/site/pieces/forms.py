# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from pieces.models import TestPiece
from django.forms import ModelForm

class EditPieceForm(ModelForm):
    """
    Form for entering a new test piece
    """
    class Meta:
        model = TestPiece
        fields = ('name', 'year', 'composer', 'arranger', 'category')