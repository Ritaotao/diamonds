import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# DATA
DATA_DIR = os.path.join(ROOT_DIR, 'data')
# MODEL
MODEL_DIR = os.path.join(ROOT_DIR, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'my_model.h5')
MODEL_SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
MODEL_WEIGHT_PATH = os.path.join(MODEL_DIR, 'weights.best.hdf5')

# Diamond fluorescence itself is a debated topic, see https://www.leibish.com/diamond-fluorescence-article-245
# [TODO] Explore how different pair of color + fluorescence may result in different price
# Now we just simplify based on UV light intensity
def map_fluorescence(x):
    if x == 'None':
        return 'None'
    elif 'Faint' in x:
        return 'Faint'
    elif 'Medium' in x:
        return 'Medium'
    elif 'Very Strong' in x:
        return 'Very Strong'
    elif 'Strong' in x:
        return 'Strong'

fluorescence = ['Very Strong', 'Strong', 'Medium', 'Faint', 'None']
# ranking: the bigger the better
ranking = {
    'clarity': ['I2', 'I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF', 'FL'],
    'color': ['K', 'J', 'I', 'H', 'G', 'F', 'E', 'D'],
    'cut': ['Good', 'Very Good', 'Ideal', 'Astor Ideal'], # https://www.bluenile.com/education/diamonds/cut
    'culet': ['Medium', 'Small', 'Very Small', 'Pointed', 'None'],
    'polish': ['Good', 'Very Good', 'Excellent'],
    'symmetry': ['Good', 'Very Good', 'Excellent']
}