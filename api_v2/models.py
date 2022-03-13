#REALLY SLOWS DOWN THE exectution time :D



from rest_framework import serializers

class Patch:
    def __init__(self,version,start,end):
        self.patch_version = version
        self.patch_start_date = start
        self.patch_end_date = end
        self.matches = []

class Match:
    def __init__(self,match_id,duration):
        self.match_id = match_id
        self.duration = duration

class Patches:
    def __init__(self,data):
        self.patches = []
        current_patch = "";
        for row in data:
            if current_patch != row[0]:
                self.patches.append(Patch(row[0],row[1],row[2]))
                current_patch = row[0]
            if(row[3] == None and row[4] == None):
                continue
            self.patches[-1].matches.append(Match(row[3],row[4]))

class MatchSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    duration = serializers.DecimalField(max_digits=None,decimal_places=2)
    class Meta:
        model = Match
        fields = ('match_id', 'duration')

class PatchSerializer(serializers.Serializer):
    patch_version = serializers.CharField()
    patch_start_date = serializers.FloatField()
    patch_end_date = serializers.FloatField()
    matches = MatchSerializer(many=True,read_only=True)
    class Meta:
        model = Patch
        fields = ('patch_version', 'patch_start_date','patch_end_date','matches')

class PatchesSerializer(serializers.Serializer):
    patches = PatchSerializer(many=True,read_only=True)
    class Meta:
        model= Patches
        fields = ("patches")

