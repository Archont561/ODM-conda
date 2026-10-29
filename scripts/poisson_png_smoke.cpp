// Test the patched upstream image adapter, not the Poisson executable's CLI.
#include "Src/PreProcessor.h"
#include "Src/Image.h"
#include <cstring>

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    const unsigned int width = 3, height = 2;
    for (unsigned int channels : {1u, 3u, 4u})
    {
        unsigned char pixels[24];
        for (unsigned int i=0; i<width*height*channels; ++i) pixels[i] = (i*37u + 11u) % 256;
        ImageWriter *writer = ImageWriter::Get(argv[1], width, height, channels);
        writer->nextRows(pixels, height);
        delete writer;
        unsigned int w=0, h=0, c=0;
        unsigned char *actual = ImageReader::Read(argv[1], w, h, c);
        bool ok = w == width && h == height && c == channels && !std::memcmp(pixels, actual, width*height*channels);
        delete[] actual;
        if (!ok) return 1;
    }
    return 0;
}
