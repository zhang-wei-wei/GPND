
import torch
from torch import nn
from torch.nn import functional as F

class VAE(nn.Module):
    def __init__(self, zsize, batch_norm_track_statisticks=True):
        super(VAE, self).__init__()

        # self.fc1 = nn.Linear(784, 400)
        # self.fc21 = nn.Linear(400, 20)
        # self.fc22 = nn.Linear(400, 20)
        # self.fc3 = nn.Linear(20, 400)
        # self.fc4 = nn.Linear(400, 784)

        # def __init__(self, c, d=128):
        # super(CGenerator, self).__init__()
        d = 128
        self.zsize = zsize
        self.deconv1 = nn.ConvTranspose2d(zsize, d * 2, 4, 1, 0)
        self.deconv1_bn = nn.BatchNorm2d(d * 2, track_running_stats=batch_norm_track_statisticks)
        self.deconv2 = nn.ConvTranspose2d(d * 2, d * 2, 4, 2, 1)
        self.deconv2_bn = nn.BatchNorm2d(d * 2, track_running_stats=batch_norm_track_statisticks)
        self.deconv3 = nn.ConvTranspose2d(d * 2, d, 4, 2, 1)
        self.deconv3_bn = nn.BatchNorm2d(d, track_running_stats=batch_norm_track_statisticks)
        self.deconv4 = nn.ConvTranspose2d(d, 1, 4, 2, 1)

        self.conv1 = nn.Conv2d(1, d // 2, 4, 2, 1)
        self.conv2 = nn.Conv2d(d // 2, d * 2, 4, 2, 1)
        self.conv2_bn = nn.BatchNorm2d(d * 2, track_running_stats=batch_norm_track_statisticks)
        self.conv3 = nn.Conv2d(d * 2, d * 4, 4, 2, 1)
        self.conv3_bn = nn.BatchNorm2d(d * 4, track_running_stats=batch_norm_track_statisticks)
        self.conv4_1 = nn.Conv2d(d * 4, zsize, 4, 1, 0)
        self.conv4_2 = nn.Conv2d(d * 4, zsize, 4, 1, 0)

    def encode(self, x):
        x = F.relu(self.conv1(x), 0.2)
        #print(x.size())
        x = F.relu(self.conv2_bn(self.conv2(x)), 0.2)
        x = F.relu(self.conv3_bn(self.conv3(x)), 0.2)
        #x = F.relu(self.conv2(x), 0.2)
        #print(x.size())
        #x = F.relu(self.conv3(x), 0.2)
        #print(x.size())
        h1 = self.conv4_1(x)
        #print(h1.size())
        h2 = self.conv4_2(x)
        return h1, h2

    def reparameterize(self, mu, logvar):
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return eps.mul(std).add_(mu)
        else:
            return mu

    def decode(self, z):
        x = z.view(-1, self.zsize, 1, 1)
        x = F.relu(self.deconv1_bn(self.deconv1(x)))
        x = F.relu(self.deconv2_bn(self.deconv2(x)))
        x = F.relu(self.deconv3_bn(self.deconv3(x)))
        x = F.tanh(self.deconv4(x)) * 0.5 + 0.5
        return x

    def forward(self, x):
        mu, logvar = self.encode(x)
        mu = mu.squeeze()
        logvar = logvar.squeeze()
        z = self.reparameterize(mu, logvar)
        return self.decode(z.view(-1, self.zsize, 1, 1)), mu, logvar

    def weight_init(self, mean, std):
        for m in self._modules:
            normal_init(self._modules[m], mean, std)


class Generator(nn.Module):
    # initializers
    def __init__(self, z_size, batch_norm_track_statisticks=True, d=128):
        super(Generator, self).__init__()
        self.deconv1_1 = nn.ConvTranspose2d(z_size, d*2, 4, 1, 0)
        self.deconv1_1_bn = nn.BatchNorm2d(d*2, track_running_stats=batch_norm_track_statisticks)
        self.deconv1_2 = nn.ConvTranspose2d(10, d*2, 4, 1, 0)
        self.deconv1_2_bn = nn.BatchNorm2d(d*2, track_running_stats=batch_norm_track_statisticks)
        self.deconv2 = nn.ConvTranspose2d(d*2, d*2, 4, 2, 1)
        self.deconv2_bn = nn.BatchNorm2d(d*2, track_running_stats=batch_norm_track_statisticks)
        self.deconv3 = nn.ConvTranspose2d(d*2, d, 4, 2, 1)
        self.deconv3_bn = nn.BatchNorm2d(d, track_running_stats=batch_norm_track_statisticks)
        self.deconv4 = nn.ConvTranspose2d(d, 1, 4, 2, 1)

    # weight_init
    def weight_init(self, mean, std):
        for m in self._modules:
            normal_init(self._modules[m], mean, std)

    # forward method
    def forward(self, input):#, label):
        x = F.relu(self.deconv1_1_bn(self.deconv1_1(input)))
        x = F.relu(self.deconv2_bn(self.deconv2(x)))
        x = F.relu(self.deconv3_bn(self.deconv3(x)))
        x = F.tanh(self.deconv4(x)) * 0.5 + 0.5

        return x


class Discriminator(nn.Module):
    # initializers
    def __init__(self, d=128):
        super(Discriminator, self).__init__()
        self.conv1_1 = nn.Conv2d(1, d//2, 4, 2, 1)
        self.conv2 = nn.Conv2d(d // 2, d*2, 4, 2, 1)
        self.conv2_bn = nn.BatchNorm2d(d*2)
        self.conv3 = nn.Conv2d(d*2, d*4, 4, 2, 1)
        self.conv3_bn = nn.BatchNorm2d(d*4)
        self.conv4 = nn.Conv2d(d * 4, 1, 4, 1, 0)

    # weight_init
    def weight_init(self, mean, std):
        for m in self._modules:
            normal_init(self._modules[m], mean, std)

    # forward method
    def forward(self, input):
        x = F.leaky_relu(self.conv1_1(input), 0.2)
        x = F.leaky_relu(self.conv2_bn(self.conv2(x)), 0.2)
        x = F.leaky_relu(self.conv3_bn(self.conv3(x)), 0.2)
        x = F.sigmoid(self.conv4(x))
        return x


class Encoder(nn.Module):
    # initializers
    def __init__(self, z_size, batch_norm_track_statisticks=True, d=128):
        super(Encoder, self).__init__()
        self.conv1_1 = nn.Conv2d(1, d//2, 4, 2, 1)
        self.conv2 = nn.Conv2d(d // 2, d*2, 4, 2, 1)
        self.conv2_bn = nn.BatchNorm2d(d*2, track_running_stats=batch_norm_track_statisticks)
        self.conv3 = nn.Conv2d(d*2, d*4, 4, 2, 1)
        self.conv3_bn = nn.BatchNorm2d(d*4, track_running_stats=batch_norm_track_statisticks)
        self.conv4 = nn.Conv2d(d * 4, z_size, 4, 1, 0)

    # weight_init
    def weight_init(self, mean, std):
        for m in self._modules:
            normal_init(self._modules[m], mean, std)

    # forward method
    def forward(self, input):
        x = F.leaky_relu(self.conv1_1(input), 0.2)
        x = F.leaky_relu(self.conv2_bn(self.conv2(x)), 0.2)
        x = F.leaky_relu(self.conv3_bn(self.conv3(x)), 0.2)
        x = self.conv4(x)
        return x


class ZDiscriminator(nn.Module):
    # initializers
    def __init__(self, z_size, d=128):
        super(ZDiscriminator, self).__init__()
        self.linear1 = nn.Linear(z_size, d*2)
        self.linear1_bn = nn.BatchNorm1d(d*2)
        self.linear2 = nn.Linear(d*2, 1)

    # weight_init
    def weight_init(self, mean, std):
        for m in self._modules:
            normal_init(self._modules[m], mean, std)

    # forward method
    def forward(self, input):
        x = F.leaky_relu((self.linear1(input)), 0.2)
        x = F.sigmoid(self.linear2(x))
        return x


def normal_init(m, mean, std):
    if isinstance(m, nn.ConvTranspose2d) or isinstance(m, nn.Conv2d):
        m.weight.data.normal_(mean, std)
        m.bias.data.zero_()
