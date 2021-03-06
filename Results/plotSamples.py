import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing


def fileToList(filename):
    temp = []
    with open(filename) as file:
        for line in file:
            try:
                temp.append(float(line.split()[1]))
            except:
                temp.append(float(line.split()[0]))
    return temp

def normalise(input):
    output = np.array(input, dtype=float)
    output = preprocessing.normalize([output])
    output = output[0]
    #output = moving_average(output, n=10)
    return output

# def moving_average(a, n=10) :
#     ret = np.cumsum(a, dtype=float)
#     ret[n:] = ret[n:] - ret[:-n]
#     return ret[n - 1:] / n    

#red = normalise(fileToList('redDye_USB2F035981__0__6.txt', True))
#green = normalise(fileToList('greenDye_USB2F035981__0__7.txt', False))
#weakRed = normalise(fileToList('weakRedDye_USB2F035981__0__8.txt', False))
#emptyCuvette = normalise(fileToList('emptyCuvette_USB2F035981__0__2.txt', False))
#bottle = normalise(fileToList('bottleWater_USB2F035981__0__5.txt', False))
#distilled = normalise(fileToList('distilledWater_USB2F035981__0__18.txt', False))
#tap = normalise(fileToList('tapWater_USB2F035981__0__4.txt', False))
#canal = normalise(fileToList('canalWater_USB2F035981__0__3.txt', False))
#canal2 = normalise(fileToList('canalWater_USB2F035981__0__10.txt', False))

#hal = normalise(fileToList('canalWater_USB2F035981__0__3.txt', True))
red = normalise(fileToList('halfStep-Red-1.txt'))
green = normalise(fileToList('halfStep-Green-1.txt'))
blue = normalise(fileToList('halfStep-Blue-1.txt'))
out = normalise(fileToList('output.txt'))
distilled = normalise(fileToList('halfStep-Distilled-3.txt'))
distilled2 = normalise(fileToList('halfStep-Distilled-4.txt'))
distilled3 = normalise(fileToList('halfStep-Distilled-5.txt'))
canal2 = normalise(fileToList('halfStep-Canal-4.txt'))
canal3 = normalise(fileToList('halfStep-Canal-3.txt'))
# green = fileToList('0Green.txt')
# #cuvette = normalise(fileToList('cuvette.txt'))

plt.xlabel('Wavelengths', fontsize = 15, style='italic')
plt.ylabel('Relative Intensities (Normalised)', fontsize = 15, style='italic')

ttl = plt.title('Comparison of spectrums for different dyes', fontsize = 20)


#plt.plot(canal, color="red")
plt.plot(red, color="red")
plt.plot(blue, color="blue")
plt.plot(green, color="green")
plt.plot(distilled3, color="aqua")
plt.plot(out, color="black")

# plt.plot(blue, color="blue")
# plt.plot(green, color="green")
# #plt.plot(cuvette, color="blue")


#plt.plot(wavelengths, red, color="red")
#plt.plot(wavelengths, green, color="green")
#plt.plot(wavelengths, weakRed, color="lightcoral")
#plt.plot(wavelengths, emptyCuvette, color="black")
#plt.plot(wavelengths, bottle, color="blue")
#plt.plot(wavelengths, distilled, color="aqua")
#plt.plot(wavelengths, tap, color="silver")
#plt.plot(wavelengths, canal, color="gold")
#plt.plot(wavelengths, canal2, color="red")
#plt.yscale('log')
plt.legend(["Red", "Blue", "Green", "De-Ionised"])
#plt.xscale('log')
#plt.gca().invert_xaxis()
plt.grid('on')
ttl.set_weight('bold')
plt.gca().spines['right'].set_color((.8,.8,.8))
plt.gca().spines['top'].set_color((.8,.8,.8))
plt.show()
