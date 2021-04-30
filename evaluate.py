import tensorflow as tf
import numpy as np
import lpips
import torch

def evaluate_lpips(sr, hr):
    lpips_alex = lpips.LPIPS(net='alex')
    sr, hr=tf.expand_dims(tf.transpose(sr, [2, 0, 1]), axis=0), tf.expand_dims(tf.transpose(hr, [2, 0, 1]), axis=0)
    return lpips_alex.forward(torch.Tensor(hr.numpy()), torch.Tensor(sr.numpy())) #Calculate LPIPS Similarity

def evaluate_psnr(sr, hr):
    def PSNR(y_true,y_pred, image_range = 1):
        mse=tf.reduce_mean( (y_true - y_pred) ** 2 )
        return 20 * log10(image_range / (mse ** 0.5))

    def log10(x):
        numerator = tf.math.log(x)
        denominator = tf.math.log(tf.constant(10, dtype=numerator.dtype))
        return numerator / denominator
    return PSNR(hr, sr)

def evaluate_ssim(sr, hr):
    return tf.image.ssim(sr, hr, max_val=1, filter_size=11,
                          filter_sigma=1.5, k1=0.01, k2=0.03)

def plot_examples(data_list, plot_size=4):
    # returns a image with all (SR, HR) pair visualized
    num_data = len(data_list)
    fig=plt.figure(figsize=(plot_size * num_data, plot_size * 2))

    for idx,x in enumerate(data_list):
        plt.subplot(2, num_data, 1 + idx)
        plt.imshow(np.clip(data_list[0],0,1))
        plt.axis('off')

        plt.subplot(2, num_data, 1 + idx + num_data)
        plt.imshow(data_list[1])
        plt.axis('off')

    fig.canvas.draw()

    image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image_from_plot = image_from_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()

    return image_from_plot

def evaluate_dataset(dataset, model, cfg):
    # evalutaes ever
    sum_LPIPS, sum_PSNR, sum_SSIM = 0, 0, 0
    data_list = []    # save all SR image for plotting

    for lr, hr in dataset:
        sr = model(lr[np.newaxis,:])[0] #Generate SR image
        
        if cfg['logging']['psnr']:
            sum_PSNR += evaluate_psnr(sr, hr)
        if cfg['logging']['ssim']:
            sum_SSIM += evaluate_ssim(sr, hr)
        if cfg['logging']['lpips']:
            sum_LPIPS += evaluate_lpips(sr, hr)
        
        if cfg['logging']['plot_samples']:
            data_list.append((sr, hr))

    num_data = len(dataset)
    logs={}
    if cfg['logging']['psnr']:
        logs['psnr'] = sum_PSNR / num_data
    if cfg['logging']['ssim']:
        logs['psnr'] = sum_SSIM / num_data
    if cfg['logging']['lpips']:
        logs['psnr'] = sum_LPIPS / num_data
    if cfg['logging']['plot_samples']:
        logs['samples'] = plot_examples(data_list)

    return logs