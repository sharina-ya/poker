import hashlib
import random
import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

#ttp - trusted third party - сервер

#protocol 3: initialization
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    return private_key, public_key


def key_to_string(key, is_private=True):
    if is_private:
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
    else:
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')


def generate_key_pairs(n):
    players = {}

    ttp_private, ttp_public = generate_key_pair()

    players['TTP'] = {
        'private': ttp_private,
        'public': ttp_public,
        'public_pem': key_to_string(ttp_public, is_private=False)
    }

    for i in range(1, n + 1):
        private, public = generate_key_pair()

        players[f'Player_{i}'] = {
            'private': private,
            'public': public,
            'public_pem': key_to_string(public, is_private=False)
        }

    return players


def digital_sign(private_key, data): #подписывает карту (карту + число) до шифровки, используется для того чтобы предотвратить подмену карты
    return private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def verify_sign(public_key, signature, data):
    """
    :param public_key: публичный ключ сервера
    :param signature: подпись сделанная сервером
    :param data: данные, которые расшифрованы (битовая строка, если нужно перевести в биты)
    :return: bool
    """
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return True

    except Exception:
        return False


#protocol 4: card shuffling
# def card_shuffling(deck, n, keys):
#     random.shuffle(deck)
#     R_0 = os.urandom(16).hex()
#     data = str(deck).encode() + R_0.encode()
#     h_TTP = hashlib.sha256(data).hexdigest()
#     ttp_signature = digital_sign(keys['TTP']['private'], h_TTP.encode())
#
#     ttp_data = {
#         'permutation': deck,
#         'salt': R_0,
#         'commitment': h_TTP,
#         'signature': ttp_signature,
#         'public_key_pem': keys['TTP']['public_pem']
#     }
#
#     players_data = list()
#     for i in range(n):
#         print(f'Игрок с номером {i + 1} тасует колоду')
#         players_data.append(player_shuffle(i + 1, h_TTP, keys[f'Player_{i + 1}']))
#         p_i = players_data[i][1]
#         signature = players_data[i][2]
#
#         verify_data = str(p_i).encode() + h_TTP.encode()
#         is_valid = verify_sign(keys[f'Player_{i + 1}']['public'], signature, verify_data)
#
#         if not is_valid:
#             print(f"Цифровая подпись игрока с номером {i + 1} некорректна")
#         else:
#             print(f"Цифровая подпись игрока с номером {i + 1} подтверждена")
#
#         new_deck = [0] * 52
#         for index in range(52):
#             new_deck[p_i[index]] = deck[index]
#
#         deck = new_deck.copy()
#
#     return deck, ttp_data, players_data


# def player_shuffle(player_id, h_ttp, players_keys):
#     deck_permutation = [i for i in range(52)] # здесь не карты, а их индексы (положение) в колоде
#     random.shuffle(deck_permutation)
#
#     data = str(deck_permutation).encode() + h_ttp.encode()
#     signature = digital_sign(players_keys['private'], data)
#
#     return (player_id, deck_permutation, signature)


#protocol 5: drawing card
def draw_card(deck, players_keys, ttp_keys): #отправить игроку зашифрованную карту и подпись (подпись не шифруется)
    if len(deck) > 0:
        R_1 = os.urandom(8).hex()
        print('Шифруем карту ', deck[-1])
        card = str(deck.pop())

        sign_data = R_1.encode() + card.encode()
        signature = digital_sign(ttp_keys['private'], sign_data)

        data = { #словарь для шифрования и отправки
            'card': card,
            'salt': R_1,
        }

        byte_data = json.dumps(data).encode()

        card_enc = players_keys['public'].encrypt( #зашифрованная информация не только об одной карте, о всем словаре
            byte_data,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                         algorithm=hashes.SHA256(),
                         label=None)
        )

        return card_enc, signature
    else:
        print("Deck is empty")


def decrypt_card(data_enc, signature, ttp_keys, players_key):
    """
    :param data_enc: зашифрованные данные полученные от сервера
    :param signature: подпись сервера
    :param ttp_keys: ключи сервера
    :param players_key: ключи игрока
    :return:
    """
    plaintext = players_key['private'].decrypt(
        data_enc,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )
    data_dec = json.loads(plaintext.decode('utf-8'))

    #расшифрованы не в виде битов
    card = data_dec['card']
    salt = data_dec['salt']

    verify_data = salt.encode() + card.encode()
    is_valid = verify_sign(ttp_keys['public'], signature, verify_data)

    if not is_valid:
        print("Цифровая подпись некорректна")
    else:
        print("Цифровая подпись подтверждена")
        return card


print('Введите количество игроков: ')
n = int(input())

print('Генерируем пары ключей...')
deck = [i for i in range(1, 53)]
keys = generate_key_pairs(n)

print('Тасуем колоду...')
# shuffled_deck, ttp_data, players_data = card_shuffling(deck, n, keys)
random.shuffle(deck)
print('Вытягиваем карту...')
card_enc, signature = draw_card(deck, keys['Player_1'], keys['TTP'])
print('Результат шифрования:\n', card_enc)
print('Цифровая подпись:\n', signature)
print('Отправляем карту пользователю, пользователь расшифровывает карту и подтвреждает цифровую подпись: ')
card = decrypt_card(card_enc, signature, keys['TTP'], keys['Player_1'])
print('Полученная карты: ', card)


