from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import datetime
from email import encoders
import supervision as sv
import numpy as np
import smtplib
import pytz
import cv2
import os

def generate_output_frame(
    image,
    detections: dict,
    show_output: bool = True
):
    """
    Args:
        image: Original input image.
        detections: Dictionary containing information about vehicle, license plate, and characters.
        show_output: Flag to determine whether to display the output frame.
    
    Description:
        Generate an output frame with visualizations and information about detections.

    Input:
        - image: Original input image.
        - detections: Dictionary containing information about vehicle, license plate, and characters.
        - show_output: Flag to determine whether to display the output frame.

    Output:
        - The output frame image with visualizations and information.
    """
    # Generate an output frame with visualizations and information about detections
    COLORS = [(0, 128, 255), (0, 255, 0), (0, 0, 255)]
    vehicle_image = None
    plate_image = None

    vehicle = detections.get("vehicle", None)
    if vehicle:
        plot_detections(image, vehicle["bbox"], COLORS[0])

    license_plate = detections.get("license_plate", None)
    if license_plate:
        vehicle_image = plot_detections(
            vehicle["image"], license_plate["bbox"], COLORS[1]
        )

    characters = detections.get("characters", None)
    if characters:
        plate_image = license_plate["image"]
        for char_bbox in characters:
            plate_image = plot_detections(plate_image, char_bbox, COLORS[2])
    # Concatenate images for visualization
    side = []
    image = cv2.resize(image, (1280, 720), interpolation=cv2.INTER_LINEAR)
    if vehicle_image is not None:
        vehicle_image = cv2.resize(
            vehicle_image, (300, 300), interpolation=cv2.INTER_LINEAR
        )
        side.append(vehicle_image)
    if plate_image is not None:
        plate_image = cv2.resize(
            plate_image, (300, 100), interpolation=cv2.INTER_LINEAR
        )
        side.append(plate_image)

    if side:
        side_img = cv2.vconcat(side)
        ini_borda_preta = side_img.shape[0]
    else:
        ini_borda_preta = 0

    borda_preta = np.zeros(shape=(720 - ini_borda_preta, 300, 3), dtype=np.uint8)
    if side:
        side_img = cv2.vconcat([side_img, borda_preta])
    else:
        side_img = borda_preta
    image = cv2.hconcat([side_img, image])

    # Add text information to the output frame
    cv2.putText(
        image,
        detections["vehicle_type"],
        (20, ini_borda_preta + 30),
        cv2.FONT_HERSHEY_DUPLEX,
        1,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        image,
        detections["plate_type"],
        (20, ini_borda_preta + 90),
        cv2.FONT_HERSHEY_DUPLEX,
        1,
        (255, 255, 255),
        2,
    )

    recognized_plate = detections.get("recognized_plate", "---")
    cv2.putText(
        image,
        recognized_plate,
        (20, ini_borda_preta + 150),
        cv2.FONT_HERSHEY_DUPLEX,
        1,
        (255, 255, 255),
        2,
    )

    # Display the output frame if required
    if show_output:
        cv2.imshow("output", image)
        cv2.waitKey(1)
    return image

def write_log(msg):
    try:
        date = datetime.now()
        with open(f'./logs/log_{date.strftime("%Y_%m_%d")}.txt', 'a+') as f:
            f.write(str(date) + ' ' + str(msg) + '\n')
    except:
        return -1
        
def calc_area(bbox):
    length = bbox[3] - bbox[1] 
    width = bbox[2] - bbox[0]
    return float(length * width)

def linear_interpolation(areas):
    first_frame = areas[0][0]
    last_frame = areas[-1][0]
    if last_frame - first_frame > len(areas):
        new_areas = []
        count_frame = first_frame
        for idx, frame in enumerate(areas):
            if frame[0] == count_frame:
                new_areas.append(frame)
                count_frame += 1
                continue
            x = count_frame
            x1 = count_frame - 1
            x2 = frame[0]
            fraction = (x - x1) / (x2 - x1)
            interpolated_area = areas[idx - 1][1] + (frame[1] - areas[idx - 1][1]) * fraction
            new_areas.append((count_frame, interpolated_area, [-1]))
            count_frame += 1
        return new_areas
    return areas

def create_video(
    frames,
    path,
    fourcc,
    fps,
    width,
    height
):
    try:
        video_writer = cv2.VideoWriter(path, fourcc = fourcc, fps = fps, frameSize = (width, height))
        for frame in frames:
            video_writer.write(frame)
        video_writer.release()
        return True
    except:
        print(f'Erro ao salvar o video do diretorio: {path}')
        return False

def send_mail(
    path,
    speed,
    key,
    sender,
    password,
    receiver
):
    try:
        mail_server = smtplib.SMTP('smtp.gmail.com', 587)
        mail_server.starttls()
        mail_server.login(sender, password)

        email = MIMEMultipart()
        email['From'] = sender
        email['To'] = receiver
        
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = now.strftime("%d/%m/%Y")
        hour = now.strftime("%H:%M:%S")
        
        email['Subject'] = f'Alerta de Excesso de Velocidade - Veículo {key}'
        email.attach(MIMEText(f'<p>Prezado(a) Administrador(a),</p><p>Gostaríamos de informar que o Veículo {key} excedeu o limite de velocidade estabelecido. A velocidade registrada foi de {speed} km/h no dia {day} às {hour}. Anexamos a gravação do momento em que a infração ocorreu para sua análise.</p><p>Atenciosamente, <p>Atala.IA</p>', 'html'))

        attachment = open(path, 'rb')
        archive = MIMEBase('application', 'octet-stream')
        archive.set_payload(attachment.read())

        encoders.encode_base64(archive)
        
        name = path.split('/')[-1]
        archive.add_header('Content-Disposition', f'attachment; filename={name}')

        attachment.close()

        email.attach(archive)

        mail_server.sendmail(email['From'], email['To'], email.as_string())
    except Exception as e:
        write_log(f'Erro ao enviar email: {e}')
    finally:
        mail_server.quit()

def create_dir(folder):
    try:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        return True
    except Exception as e:
        return False

def create_file(
    folder,
    file
):
    try:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        
        file = os.path.join(folder, file)
        
        if os.path.isfile(file):
            os.remove(file)
        with open(file, 'a+') as f:
            f.write('Id;Speed(km/h)' + '\n')
    except Exception as e:
        raise Exception(f'Erro ao criar arquivo: {e}')