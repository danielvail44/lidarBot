using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using AForge.Video;
using System.Net.Http;
using System.Diagnostics;
using System.IO;
using System.Timers;



namespace ControlCenter
{
    public partial class Form1 : Form
    {

        MJPEGStream stream;
        private static readonly HttpClient client = new HttpClient();
        Process pythonProgram;


        public Form1()
        {
            InitializeComponent();
            KeyPreview = true;
            stream = new MJPEGStream("http://10.42.0.1:8000/stream.mjpg");
            stream.NewFrame += stream_NewFrame;
            stream.Start();
            pythonProgram = run_cmd("C:\\Users\\danie\\source\\repos\\ControlCenter\\ControlCenter\\uart.py", "");
            System.Timers.Timer imageUpdater = new System.Timers.Timer();
            imageUpdater.Elapsed += new ElapsedEventHandler(updateScan);
            imageUpdater.Interval = 1000;
            imageUpdater.Enabled = true;

            this.KeyDown += new KeyEventHandler(Form1_KeyDown);
            this.KeyUp += new KeyEventHandler(Form1_KeyUp);
            FormClosing += Form1_FormClosing;

        }

        void stream_NewFrame(object sender, NewFrameEventArgs eventArgs)
        {
            Bitmap bmp = (Bitmap)eventArgs.Frame.Clone();
            pictureBox1.Image = bmp;
        }

        void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            pythonProgram.Kill();
            stream.Stop();
        }


        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }

        private void button1_MouseDown(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/forward.html");
        }

        private void button1_MouseUp(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/forward_stop.html");
        }



        private void button2_MouseDown(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/backward.html");
        }

        private void button2_MouseUp(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/backward_stop.html");
        }

        private void button3_MouseDown(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/left.html");
        }

        private void button3_MouseUp(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/left_stop.html");
        }

        private void button4_MouseDown(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/right.html");
        }

        private void button4_MouseUp(object sender, MouseEventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/right_stop.html");
        }

        private void button5_Click(object sender, EventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/scan_start.html");

        }

        private Process run_cmd(string cmd, string args)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "C:\\Users\\danie\\AppData\\Local\\Programs\\Python\\Python37\\python.exe";
            start.Arguments = string.Format("{0} {1}", cmd, args);
            start.UseShellExecute = false;
            start.RedirectStandardOutput = false;
            start.CreateNoWindow = false;
            return Process.Start(start);
            
        }

        private void updateScan(object srouce, ElapsedEventArgs e)
        {
            try
            {
                Image image = Image.FromStream(new MemoryStream(File.ReadAllBytes("C:\\Users\\danie\\source\\repos\\ControlCenter\\ControlCenter\\plot.png")));
                pictureBox2.Image = image;

            }
            catch (Exception f) { };



        }

        private void Form1_KeyDown(object sender, KeyEventArgs e)
        {
            e.SuppressKeyPress = true;
            switch (e.KeyCode)
            {
                case Keys.W:
                    client.GetStringAsync("http://10.42.0.1:8000/forward.html");
                    break;
                case Keys.S:
                    client.GetStringAsync("http://10.42.0.1:8000/backward.html");
                    break;
                case Keys.A:
                    client.GetStringAsync("http://10.42.0.1:8000/left.html");
                    break;
                case Keys.D:
                    client.GetStringAsync("http://10.42.0.1:8000/right.html");
                    break;
            }
            e.SuppressKeyPress = true;
        }

        private void Form1_KeyUp(object sender, KeyEventArgs e)
        {
            e.SuppressKeyPress = true;
            switch (e.KeyCode)
            {
                case Keys.W:
                    client.GetStringAsync("http://10.42.0.1:8000/forward_stop.html");
                    break;
                case Keys.S:
                    client.GetStringAsync("http://10.42.0.1:8000/backward_stop.html");
                    break;
                case Keys.A:
                    client.GetStringAsync("http://10.42.0.1:8000/left_stop.html");
                    break;
                case Keys.D:
                    client.GetStringAsync("http://10.42.0.1:8000/right_stop.html");
                    break;
            }
            
        }

        private void button6_Click(object sender, EventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/scan_stop.html");
        }


        private void button7_Click(object sender, EventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/manual.html");
        }

        private void button8_Click(object sender, EventArgs e)
        {
            client.GetStringAsync("http://10.42.0.1:8000/auto.html");
        }
    }
}
