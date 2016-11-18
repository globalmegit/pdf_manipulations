import imghdr
import os
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


CANVAS_SIZE_A4_PORTRAIT = (8.26 * inch, 11.69 * inch)
CANVAS_SIZE_A4_LANDSCAPE = (11.69 * inch, 8.26 * inch)
CANVAS_SIZE_US_LETTER_PORTRAIT = (8.50 * inch, 11.00 * inch)
CANVAS_SIZE_US_LETTER_LANDSCAPE = (11.00 * inch, 8.50 * inch)


def print_usage(exit=False):
	print("Create PDF files")
	print("Usage: ")
	print("    python createpdf.py /directory/path portrait")
	print("    python createpdf.py /directory/path landscape")
	if exit:
		sys.exit(1)


def get_os_path(root_dir, path):
	root = os.path.abspath(root_dir)
	os_path = to_os_path(path, root)
	return os_path


def to_os_path(path, root=''):
	parts = path.strip('/').split('/')
	parts = [p for p in parts if p != '']
	path = os.path.join(root, *parts)
	return path


def make_pdf_canvas(pdf_path, output_format):
	canvas_size_type = CANVAS_SIZE_US_LETTER_PORTRAIT if output_format == "portrait" else CANVAS_SIZE_US_LETTER_LANDSCAPE
	margin = 0.25 * inch
	width, height = canvas_size_type
	c = canvas.Canvas(pdf_path, pagesize=canvas_size_type)
	if output_format == "portrait":
		first_x = margin
		first_y = height / 2.0 + 0.5 * margin
		first_width = width - 2 * margin
		first_height = height / 2.0 - 2 * margin

		second_x = margin
		second_y = margin
		second_width = first_width
		second_height = first_height

		first_anchor = "c"
		second_anchor = "c"
	else:
		first_x = margin
		first_y = margin
		first_width = width / 2.0 - 1.5 * margin
		first_height = height - 2 * margin

		second_x = width / 2.0 + 0.5 * margin
		second_y = first_y
		second_width = first_width
		second_height = first_height

		first_anchor = "c"
		second_anchor = "c"
	return (
		c, first_x, first_y, first_width, first_height, first_anchor,
		second_x, second_y, second_width, second_height, second_anchor
	)


def main(argv):
	if len(argv) < 2 or len(argv) > 3:
		print_usage(exit=True)

	input_path = argv[0]
	output_format = str(argv[1]).strip()
	base_dir_name = "EN"

	if not os.path.isdir(input_path):
		print("Directory '{}' does not exist.".format(input_path))
		sys.exit(1)

	if output_format not in ("portrait", "landscape"):
		print("Output format should be either 'portrait' or 'landscape'.".format(input_path))
		sys.exit(1)

	if len(argv) == 3:
		base_dir_name = argv[2]

	input_dir = get_os_path(input_path, "")
	for name in os.listdir(input_dir):
		os_path = os.path.join(input_dir, name)
		# skip over broken symlinks in listing
		if not os.path.exists(os_path):
			print("{} does not exist".format(os_path))
			continue
		elif not os.path.isdir(os_path):
			print("{} not a directory".format(os_path))
			continue

		if base_dir_name != name:
			base_os_path = os.path.join(input_dir, base_dir_name)
			os_path = os.path.join(input_dir, name)
			pdf_path = get_os_path(os_path, name + ".pdf")
			print("\nMaking {}".format(pdf_path))
			canvas_settings = make_pdf_canvas(pdf_path, output_format)
			pdf_canvas = canvas_settings[0]
			first_x, first_y, first_width, first_height, first_anchor = canvas_settings[1:6]
			second_x, second_y, second_width, second_height, second_anchor = canvas_settings[6:]

			for fname in sorted(os.listdir(os_path)):
				base_fname_path = os.path.join(base_os_path, fname)
				fname_path = os.path.join(os_path, fname)

				# omit created PDF files
				if pdf_path == fname_path:
					continue

				# skip not existed images
				if os.path.exists(base_fname_path):
					if imghdr.what(base_fname_path):
						print(base_fname_path)
					else:
						print("{} - is not image file".format(base_fname_path))
						continue
				else:
					print("{} - does not exist".format(base_fname_path))
					continue
				if os.path.exists(fname_path):
					if imghdr.what(fname_path):
						print(fname_path)
					else:
						print("{} - is not image file".format(fname_path))
						continue
				else:
					print("{} - does not exist".format(fname_path))
					continue
				pdf_canvas.drawImage(base_fname_path, first_x, first_y, first_width, first_height, anchor=first_anchor, preserveAspectRatio=True)
				pdf_canvas.drawImage(fname_path, second_x, second_y, second_width, second_height, anchor=second_anchor, preserveAspectRatio=True)
				pdf_canvas.showPage()
			pdf_canvas.save()


if __name__ == '__main__':
	main(sys.argv[1:])
