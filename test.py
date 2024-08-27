class Xisob:
    def __init__(self):
        self.ommaviy = "Bu ommaviy"
        self._himoyalangan = "Bu himoyalangan"
        self.__shaxsiy = "Bu shaxsiy"

    def ommaviy_metod(self):
        return "Bu ommaviy metod"

    def _himoyalangan_metod(self):
        return "Bu himoyalangan metod"

    def __shaxsiy_metod(self):
        return "Bu shaxsiy metod"


# Classni ishlatamiz
x = Xisob()

# Ommaviy a'zolarga kirish
print(x.ommaviy)  # Ishlaydi
print(x.ommaviy_metod())  # Ishlaydi

# Himoyalangan a'zolarga kirish
# print(x._himoyalangan)  # Ishlaydi, lekin odatda bunday qilinmaydi
# print(x._himoyalangan_metod())  # Ishlaydi, lekin odatda bunday qilinmaydi

# Shaxsiy a'zolarga kirish
# print(x.__shaxsiy)  # AttributeError chiqaradi
# print(x.__shaxsiy_metod())  # AttributeError chiqaradi

# Shaxsiy a'zolarga kirishning aylanma yo'li
# print(x._Xisob__shaxsiy)  # Ishlaydi, lekin juda kam hollarda ishlatiladi
# print(x._Xisob__shaxsiy_metod())  # Ishlaydi, lekin juda kam hollarda ishlatiladi
# a = (x for i in range(10))
# print(a)
