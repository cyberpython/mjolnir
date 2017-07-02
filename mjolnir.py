import os
import sys
import shutil
import zipfile
import tarfile
import fileinput
import subprocess
import platform
import shlex
import logging
import xml.etree.ElementTree as ET
from logging.config import fileConfig

fileConfig('mjolnir.ini')

# create_dir
# delete_dir
# copy_dir
# copy_file
# unzip
# replace_text
# exec_cmd

class Mjolnir:
    logger = logging.getLogger('Mjolnir')

    @staticmethod
    def handle_delete_dir_error(func, path, exception_info):
        Mjolnir.logger.error("Failed to remove dir: %s" % path)


    def create_dir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                Mjolnir.logger.info("Created dir: %s" % path )
        except Exception as e:
            Mjolnir.logger.error('Error while trying to create %s' % path)
            Mjolnir.logger.exception(e)

    def delete_dir(self, path):
        Mjolnir.logger.info("Delete dir: %s" % path)
        shutil.rmtree(path, onerror=Mjolnir.handle_delete_dir_error)

    def copy_dir(self, src, dst, symlinks=False, ignore=None):
        Mjolnir.logger.info("Recursively copying dir: %s to %s" % (src, dst))
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                self.copy_dir(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        Mjolnir.logger.info("Done copying dir: %s to %s" % (src, dst))

    def copy_file(self, src, dst):
        if os.path.isfile(src):
            shutil.copy(src, dst)
            Mjolnir.logger.info("Copied: %s to: %s" % (src, dst))
        else:
            Mjolnir.logger.error("Not a file: %s" % src)

    def unzip(self, zip_file_path, dst_dir):
        Mjolnir.logger.info("Extract: %s to %s" % (zip_file_path, dst_dir))
        zip_file = zipfile.ZipFile(zip_file_path, 'r')
        zip_file.extractall(dst_dir)
        zip_file.close()
        Mjolnir.logger.info("Extracted: %s to %s" % (zip_file_path, dst_dir))

    def untar(self, tar_file_path, dst_dir):
        Mjolnir.logger.info("Extract: %s to %s" % (tar_file_path, dst_dir))
        if (tar_file_path.endswith("tar.gz")):
            tar_file = tarfile.open(tar_file_path, "r:gz")
            tar_file.extractall(path=dst_dir)
            tar_file.close()
        elif (tar_file_path.endswith("tar")):
            tar_file = tarfile.open(tar_file_path, "r:")
            tar_file.extractall()
            tar_file.close()
        Mjolnir.logger.info("Extracted: %s to %s" % (tar_file_path, dst_dir))

    def replace_text(self, file_path, search_for, replace_with):
        with fileinput.FileInput(file_path, inplace=True, backup='.bak') as file:
            for line in file:
                print(line.replace(search_for, replace_with), end='')
            Mjolnir.logger.info("Replaced: `%s` to: `%s` in: %s" % (search_for, replace_with, file_path))

    def exec_cmd(self, cmd_and_args, cwd=".", shell=True):
        Mjolnir.logger.info("Execute: %s in %s" % (' '.join(cmd_and_args), cwd))
        ret_code = subprocess.call(cmd_and_args, shell=shell, cwd=cwd)
        if ret_code != 0:
            Mjolnir.logger.error("Execution of %s failed with return code %d" % (' '.join(cmd_and_args), ret_code))

    def set_env_var(self, env_var, value, append=True):
        Mjolnir.logger.info("Set environment variable `%s` to `%s`" % (env_var, value))
        osname = platform.system()
        val = value
        if osname == 'Windows':
            if append:
                val = os.environ[env_var]+value
            # os.system("SETX %s %s" % (env_var, val))
            ret_code = subprocess.call(["SETX", env_var, val], shell=True)
            if ret_code != 0:
                Mjolnir.logger.error("Failed to set env var `%s` to `%s`" % (env_var, val))
        elif osname == 'Linux':
            Mjolnir.logger.error("Setting environment variables on %s is not supported yet." % osname)
        else:
            Mjolnir.logger.error("Setting environment variables on %s is not supported yet." % osname)
        os.environ[env_var] = val

    def parse_and_run(self, input_file):

        tree = ET.parse(input_file)
        root = tree.getroot()
        for child in root:
            if child.tag == 'create_dir':
                path = child.attrib['path']
                self.create_dir(path)
            elif child.tag == 'delete_dir':
                path = child.attrib['path']
                self.delete_dir(path)
            elif child.tag == 'copy_dir':
                src = child.attrib['src']
                dst = child.attrib['dst']
                self.copy_dir(src, dst)
            elif child.tag == 'copy_file':
                src = child.attrib['src']
                dst = child.attrib['dst']
                self.copy_file(src, dst)
            elif child.tag == 'unzip':
                fpath = child.attrib['file']
                dst = child.attrib['dst']
                self.unzip(fpath, dst)
            elif child.tag == 'untar':
                fpath = child.attrib['file']
                dst = child.attrib['dst']
                self.untar(fpath, dst)
            elif child.tag == 'replace_text':
                fpath = child.attrib['file']
                search_for= child.attrib['search_for']
                replace_with = child.attrib['replace_with']
                self.replace_text(fpath, search_for, replace_with)
            elif child.tag == 'exec':
                cmd_str = child.attrib['cmd']
                cwd = child.attrib['cwd']
                cmd = shlex.split(cmd_str)
                self.exec_cmd(cmd, cwd, shell=True)
            elif child.tag == 'set_env':
                env_var = child.attrib['var']
                value = child.attrib['value']
                append = child.attrib['append']
                self.set_env_var(env_var, value, append.lower() == 'yes')

if __name__ == '__main__':

    if len(sys.argv) < 2:
        logging.getLogger().error('Incorrect usage! The recipe file path should be passed as a command-line argument.')
        sys.exit(1)

    mjolnir = Mjolnir()
    mjolnir.parse_and_run(sys.argv[1])